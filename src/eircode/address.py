from difflib import SequenceMatcher

from cached_property import cached_property
import requests

from eircode.eircode import Eircode


class Addresses():

    def __init__(self):
        self._data = []

    def append(self, address):
        self._data.append(address)

    def ordered_best_fit(self, name):
        return sorted(
            [(i.match_score(name), i) for i in self._data],
            key=lambda i: i[0],
            reverse=True
        )


class Address():

    def __init__(self, address, **kwargs):
        self.input_address = address

        self.display_name = kwargs.get('display_name', None)
        self.link = kwargs.get('link', None)
        self._eircode = kwargs.get('eircode', None)
        self.set()

    def set(self):
        base_identity = 'https://api-finder.eircode.ie/Latest/findergetidentity'

        identity_response = requests.get(base_identity).json()

        base_url = 'https://api-finder.eircode.ie/Latest/finderfindaddress'
        params = {
            'key': identity_response['key'],
            'address': self.input_address,
            'language': 'en',
            'geographicAddress': True,
            'clientVersion': None
        }

        resp = requests.get(base_url, params=params).json()

        if 'postcode' in resp:
            self._eircode = resp['postcode']
            self.display_name = self.input_address
            return

        options = resp['options']

        if options:
            addresses = Addresses()
            for option in options:
                addresses.append(
                    Address(
                        display_name=option['displayName'],
                        link=option['links'][0]['href']
                    )
                )

            for address in addresses.ordered_best_fit(self.name):
                try:
                    self.display_name = address[1].eircode_data['display_name']
                    self._eircode = address[1].eircode_data['eircode']
                except ValueError:
                    pass
        else:
            print('TODO: use the autocomplete to see if we can get something')

    def match_score(self, name):
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
        data = requests.get(self.link).json()
        if data['options']:
            addresses = Addresses()
            for option in data['options']:
                addresses.append(
                    Address(
                        display_name=option['displayName'],
                        link=option['links'][0]['href']
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
