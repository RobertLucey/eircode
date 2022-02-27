import urllib

import requests
from requests_ip_rotator import ApiGateway


class Proxy():

    def __init__(self, skip_setup=False):
        self.gateway = None
        self.session = None

        self._is_setup = False

        if not skip_setup:
            self.setup()

    def setup(self, force=False):
        if not force and self._is_setup:
            return

        self.gateway = ApiGateway(
            'https://api-finder.eircode.ie',
            regions=['eu-west-1']
        )
        self.gateway.start()

        self.session = requests.Session()
        self.session.mount(
            'https://api-finder.eircode.ie',
            self.gateway
        )

        self._is_setup = True

    def get(self, url, params={}):
        try:
            return self.session.get(
                url + '?' + urllib.parse.urlencode(params)
            )
        except:
            self.setup(force=True)
            return self.get(url, params=params)

    def shutdown(self):
        self.gateway.shutdown()
