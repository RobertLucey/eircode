from eircode.constants import ROUTING_KEYS_TOWNS_MAP, ROUTING_KEYS_COUNTY_MAP


class Eircode():

    def __init__(self, eircode):
        self.eircode = eircode

    @property
    def routing_key(self):
        return self.eircode[:3]

    @property
    def unique_identifier(self):
        return self.eircode[3:]

    @property
    def county(self):
        return ROUTING_KEYS_COUNTY_MAP[self.routing_key]

    @property
    def towns(self):
        return ROUTING_KEYS_TOWNS_MAP[self.routing_key]
