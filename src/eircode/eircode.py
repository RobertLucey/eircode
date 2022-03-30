from eircode.constants import ROUTING_KEYS_TOWNS_MAP, ROUTING_KEYS_COUNTY_MAP


class Eircode():

    def __init__(self, eircode):
        self.eircode = eircode
        self.validate()

    def validate(self):
        if not isinstance(self.eircode, str):
            raise ValueError('Eircode must be a str')

        if not len(self.eircode) == 7:
            raise ValueError('Eircode must have 7 chars')

        if self.routing_key not in ROUTING_KEYS_TOWNS_MAP:
            raise ValueError('Routing key is not valid')

        if not self.unique_identifier.isalnum():
            raise ValueError('Eircode unique identifier must be hex')

    def __repr__(self):
        return f'Eircode({self.eircode})'

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
        '''
        Gives a list of towns or areas that the eircode may
        be in given the routing key
        '''
        return ROUTING_KEYS_TOWNS_MAP[self.routing_key]

    def serialize(self):
        return {
            'routing_key': self.routing_key,
            'unique_identifier': self.unique_identifier,
            'eircode': self.eircode,
            'county': self.county,
            'towns': self.towns
        }
