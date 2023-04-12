from unittest import TestCase

from eircode.eircode import Eircode


class EircodeTest(TestCase):
    def test_validate(self):
        with self.assertRaises(ValueError):
            # must be str
            Eircode(1234567)
        with self.assertRaises(ValueError):
            # must have 7 chars
            Eircode("D14AAA")
        with self.assertRaises(ValueError):
            # bad routing key
            Eircode("1234567")
        with self.assertRaises(ValueError):
            # not alphanum
            Eircode("D14AAA!")

    def test_repr(self):
        self.assertEqual(str(Eircode("D14AAAA")), "Eircode(D14AAAA)")

    def test_routing_key(self):
        self.assertEqual(Eircode("D14AAAA").routing_key, "D14")

    def test_unique_identifier(self):
        self.assertEqual(Eircode("D14AAAA").unique_identifier, "AAAA")

    def test_county(self):
        self.assertEqual(Eircode("D14AAAA").county, "Dublin")

    def test_towns(self):
        self.assertEqual(Eircode("D14AAAA").towns, ["Dublin 14"])

    def test_serialize(self):
        self.assertEqual(
            Eircode("D14AAAA").serialize(),
            {
                "county": "Dublin",
                "eircode": "D14AAAA",
                "routing_key": "D14",
                "towns": ["Dublin 14"],
                "unique_identifier": "AAAA",
            },
        )
