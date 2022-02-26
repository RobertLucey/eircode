from eircode.constants import ROUTING_KEYS_TOWNS_MAP, ROUTING_KEYS_COUNTY_MAP


class Eircode():

    def __init__(self, eircode):
        self.eircode = eircode

    def __repr__(self):
        return f'Eircode({self.eircode})'

    @property
    def routing_key(self):
        if not self.eircode:
            return None
        return self.eircode[:3]

    @property
    def unique_identifier(self):
        if not self.eircode:
            return None
        return self.eircode[3:]

    @property
    def county(self):
        if not self.eircode:
            return None
        return ROUTING_KEYS_COUNTY_MAP[self.routing_key]

    @property
    def towns(self):
        if not self.eircode:
            return None
        return ROUTING_KEYS_TOWNS_MAP[self.routing_key]

    def serialize(self):
        return {
            'routing_key': self.routing_key,
            'unique_identifier': self.unique_identifier,
            'eircode': self.eircode,
            'county': self.county,
            'towns': self.towns
        }
