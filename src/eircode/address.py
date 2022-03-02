from difflib import SequenceMatcher
import urllib

from cached_property import cached_property
import requests

from eircode.eircode import Eircode
from eircode.constants import (
    IDENTITY_URL_PATH,
    EIRCODE_FINDER_URL_PATH
)
from eircode.proxy import Proxy

proxy_cli = Proxy(skip_setup=True)


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
        '''
        self.input_address = address

        self.display_name = kwargs.get('display_name', None)
        self.link = kwargs.get('link', None)
        self._eircode = kwargs.get('eircode', None)

        self.proxy = kwargs.get('proxy', False)

        if not kwargs.get('skip_set', False):
            self.set(
                throw_ex=kwargs.get('throw_ex', False),
                reverse=kwargs.get('reverse', False),
            )

    def set(self, throw_ex=True, reverse=False):

        if self.proxy:

            self.proxy = True

            try:
                proxy_cli.setup()
            except:
                raise Exception('Could not set up proxy cli. Go to here for details: https://github.com/Ge0rg3/requests-ip-rotator')

            identity_response = proxy_cli.get(IDENTITY_URL_PATH).json()

            params = {
                'key': identity_response['key'],
                'address': self.input_address,
                'language': 'en',
                'geographicAddress': True,
                'clientVersion': None
            }

            finder_response = proxy_cli.get(
                EIRCODE_FINDER_URL_PATH + '?' + urllib.parse.urlencode(params)
            )

        else:
            identity_response = requests.get(IDENTITY_URL_PATH).json()
            params = {
                'key': identity_response['key'],
                'address': self.input_address,
                'language': 'en',
                'geographicAddress': True,
                'clientVersion': None
            }

            finder_response = requests.get(
                EIRCODE_FINDER_URL_PATH,
                params=params
            )

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
                print(f'Cannot search: {finder_response["error"]["text"]}')
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
                        proxy=self.proxy
                    )
                )

            for address in addresses.ordered_best_fit(self.input_address):
                try:
                    self.display_name = address[1].eircode_data['display_name']
                    self._eircode = address[1].eircode_data['eircode']
                except ValueError:
                    pass
        else:
            print('TODO: use the autocomplete to see if we can get something')

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
            data = proxy_cli.get(self.link).json()
        else:
            data = requests.get(self.link).json()

        data = requests.get(self.link).json()
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

            for address in addresses.ordered_best_fit(self.display_name):
                try:
                    if isinstance(address[1].eircode_data, str):
                        return {
                            'eircode': address[1].eircode_data,
                            'display_name': address[1].display_name
                        }
                    else:
                        return address[1].eircode_data
                except ValueError:
                    pass
        else:
            if data['result']['text'] == 'IncompleteAddressEntered':
                raise ValueError('Must go back')
            elif data['result']['text'] == 'NonUniqueAddress':
                raise ValueError('Must go back')
            else:
                return {
                    'eircode': data['postcode'],
                    'display_name': self.display_name
                }
