from unittest import TestCase

from eircode.address import Address, Addresses


class AddressesTest(TestCase):

    def test_append(self):
        addresses = Addresses()
        addresses.append(Address('', display_name='something', skip_set=True))

        self.assertEqual(len(addresses._data), 1)

    def test_ordered_best_fit(self):
        addresses = Addresses()
        addresses.append(Address('', display_name='something', skip_set=True))
        addresses.append(Address('', display_name='something else', skip_set=True))
        addresses.append(Address('', display_name='blah something', skip_set=True))

        self.assertEqual(
            addresses.ordered_best_fit('blahblah')[0][1].display_name,
            'blah something'
        )


class AddressTest(TestCase):

    def test_match_score(self):
        self.assertEqual(
            Address('', display_name='something', skip_set=True).match_score(
                Address('', display_name='something', skip_set=True)
            ),
            1
        )

        self.assertEqual(
            Address('', display_name='something', skip_set=True).match_score(
                Address('', display_name='aaaaaa', skip_set=True)
            ),
            0
        )

        self.assertGreater(
            Address('', display_name='something', skip_set=True).match_score(
                Address('', display_name='some', skip_set=True)
            ),
            0.5
        )

    def test_eircode(self):
        self.assertEqual(
            Address(
                '',
                eircode='D14AAAA',
                skip_set=True
            ).eircode.serialize(),
            {
                'county': 'Dublin',
                'eircode': 'D14AAAA',
                'routing_key': 'D14',
                'towns': ['Dublin 14'],
                'unique_identifier': 'AAAA'
            }
        )

    def test_serialize(self):
        self.assertEqual(
            Address(
                '',
                display_name='something',
                eircode='D14AAAA',
                skip_set=True
            ).serialize(),
            {
                'display_name': 'something',
                'eircode': {
                    'county': 'Dublin',
                    'eircode': 'D14AAAA',
                    'routing_key': 'D14',
                    'towns': ['Dublin 14'],
                    'unique_identifier': 'AAAA'
                },
                'link': None}
        )
