from difflib import SequenceMatcher
import urllib

from cached_property import cached_property
import requests

from eircode.logging import logger
from eircode.eircode import Eircode
from eircode.constants import (
    IDENTITY_URL_PATH,
    EIRCODE_FINDER_URL_PATH
)
from eircode.proxy import proxy


class Addresses():

    def __init__(self):
        self._data = []

    def append(self, address):
        self._data.append(address)

    def ordered_best_fit(self, name):
        if isinstance(name, Address):
            name = name.display_name

        return sorted(
            [(i.match_score(name), i) for i in self._data],
            key=lambda i: i[0],
            reverse=True
        )


class Address():

    def __init__(self, address, **kwargs):
        '''

        :param address: The address you're searching for
        :kwargs display_name (optional): The display name found on eircode.ie
        :kwargs link (optional): The link that was used to get the info
        :kwargs eircode (optional): The eircode string
        :kwargs proxy (optional): To proxy requests to the eircode api or not
        :kwargs throw_ex (optional): To throw exceptions or gracefully fail
        :kwargs reverse (optional): True if the input is a eircode
            rather than an address
        '''
        self.input_address = address

        self.display_name = kwargs.get('display_name', None)
        self.link = kwargs.get('link', None)
        self._eircode = kwargs.get('eircode', None)

        self.proxy = kwargs.get('proxy', False)
        self.throw_ex = kwargs.get('throw_ex', False)

        if not kwargs.get('skip_set', False):
            self.set(
                throw_ex=self.throw_ex,
                reverse=kwargs.get('reverse', False),
            )

    def set(self, throw_ex=True, reverse=False):
        '''

        :kwargs throw_ex (optional): To throw exceptions or gracefully fail
        :kwargs reverse (optional): True if the input is a eircode
            rather than an address
        '''
        if self.proxy:

            try:
                proxy.setup()
            except:
                raise Exception(
                    'Could not set up proxy cli. Go to here for details: https://github.com/Ge0rg3/requests-ip-rotator'
                )

            identity_response = proxy.get(IDENTITY_URL_PATH).json()
            while 'key' not in identity_response:
                identity_response = proxy.get(IDENTITY_URL_PATH).json()

            params = {
                'key': identity_response['key'],
                'address': self.input_address,
                'language': 'en',
                'geographicAddress': True,
                'clientVersion': None
            }

            try:
                finder_response = proxy.get(
                    EIRCODE_FINDER_URL_PATH + '?' + urllib.parse.urlencode(params)
                )
            except ValueError as ex:
                logger.error(
                    'Cannot search: %s' % (ex,)
                )
                return

        else:
            identity_response = requests.get(IDENTITY_URL_PATH).json()
            params = {
                'key': identity_response['key'],
                'address': self.input_address,
                'language': 'en',
                'geographicAddress': True,
                'clientVersion': None
            }

            try:
                finder_response = requests.get(
                    EIRCODE_FINDER_URL_PATH,
                    params=params
                )
            except ValueError as ex:
                logger.error(
                    'Cannot search: %s' % (ex,)
                )
                return

        finder_response = finder_response.json()

        if reverse:
            self._eircode = self.input_address
            self.display_name = ', '.join(finder_response['postalAddress'])
            return

        if 'postcode' in finder_response:
            self._eircode = finder_response['postcode']
            self.display_name = self.input_address
            return

        if finder_response.get('error', {}).get('code', None) == 403:
            if throw_ex:
                raise Exception(finder_response['error']['text'])
            else:
                logger.error(
                    f'Cannot search: {finder_response["error"]["text"]}'
                )
                return

        if 'options' not in finder_response:
            logger.error(
                f'options not found in {finder_response}'
            )
            return

        options = finder_response['options']

        if options:
            addresses = Addresses()
            for option in options:
                addresses.append(
                    Address(
                        option['displayName'],
                        display_name=option['displayName'],
                        link=option['links'][0]['href'],
                        skip_set=True,
                        proxy=self.proxy,
                        throw_ex=self.throw_ex
                    )
                )

            ordered_best = addresses.ordered_best_fit(self.input_address)
            if ordered_best:
                address = ordered_best[0][1]
                try:
                    self.display_name = address.eircode_data['display_name']
                    self._eircode = address.eircode_data['eircode']
                except ValueError as ex:
                    logger.error('Not setting eircode values: %s' % (ex,))
        else:
            logger.warning(
                'TODO: use the autocomplete to see if we can get something'
            )

    def match_score(self, name):
        if isinstance(name, Address):
            name = name.display_name

        return SequenceMatcher(
            None,
            self.display_name.lower(),
            name.lower()
        ).ratio()

    def serialize(self):
        return {
            'display_name': self.display_name,
            'link': self.link,
            'eircode': self.eircode.serialize()
        }

    @property
    def eircode(self):
        return Eircode(self._eircode)

    @cached_property
    def eircode_data(self):
        if self.proxy:
            data = proxy.get(self.link).json()
        else:
            data = requests.get(self.link).json()

        if data.get('error', {}).get('code', None) == 403:
            raise ValueError(data['error']['text'])

        if 'options' not in data:
            raise ValueError('Could not get options from data: %s' % (data,))

        if data['options']:
            addresses = Addresses()
            for option in data['options']:
                addresses.append(
                    Address(
                        option['displayName'],
                        display_name=option['displayName'],
                        link=option['links'][0]['href'],
                        skip_set=True,
                        proxy=self.proxy
                    )
                )

            ordered_best = addresses.ordered_best_fit(self.display_name)
            if ordered_best:
                address = ordered_best[0][1]
                if address.link == self.link:
                    raise ValueError('Cyclical address lookup, exiting early')
                try:
                    if isinstance(address.eircode_data, str):
                        return {
                            'eircode': address.eircode_data,
                            'display_name': address.display_name
                        }
                    else:
                        return address.eircode_data
                except ValueError:
                    raise ValueError(
                        'Best eircode option is not good, can try more options'
                    )
        else:
            if data['result']['text'] in {
                'IncompleteAddressEntered',
                'NonUniqueAddress',
                'PostcodeNotAvailable'
            }:
                raise ValueError(data['result']['text'])
            else:
                if 'postcode' in data:
                    return {
                        'eircode': data['postcode'],
                        'display_name': self.display_name
                    }
                raise ValueError('Could not find postcode in response: %s' % (data,))
