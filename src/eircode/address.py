from difflib import SequenceMatcher

from cached_property import cached_property
import requests


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

    def __init__(self, *args, **kwargs):
        self.display_name = kwargs['display_name']
        self.link = kwargs['link']

    @staticmethod
    def get(name):
        base_identity = 'https://api-finder.eircode.ie/Latest/findergetidentity'

        identity_response = requests.get(base_identity).json()

        base_url = 'https://api-finder.eircode.ie/Latest/finderfindaddress'
        params = {
            'key': identity_response['key'],
            'address': name,
            'language': 'en',
            'geographicAddress': True,
            'clientVersion': None
        }

        resp = requests.get(base_url, params=params).json()

        if 'postcode' in resp:
            return {
                'eircode': resp['postcode'],
                'display_name': name
            }

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

            for address in addresses.ordered_best_fit(name):
                try:
                    return address[1].eircode
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
            'eircode': self.eircode,
            'link': self.link
        }

    @cached_property
    def eircode(self):
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
                    if isinstance(address[1].eircode, str):
                        return {
                            'eircode': address[1].eircode,
                            'display_name': address[1].display_name
                        }
                    else:
                        return address[1].eircode
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
