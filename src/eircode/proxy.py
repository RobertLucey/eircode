import urllib
import urllib.parse
import random

import requests
from requests_ip_rotator import ApiGateway

from eircode.logging import logger


class Proxy():

    def __init__(self, skip_setup=False, site=None):
        self.gateway = None
        self.session = None

        self.site = site if site is not None else 'https://api-finder.eircode.ie'

        self._is_setup = False

        if not skip_setup:
            self.setup()

    def setup(self, force=False):
        if not force and self._is_setup:
            return

        self.gateway = ApiGateway(
            self.site
        )
        self.gateway.shutdown()
        self.gateway.start(force=True)

        self.session = requests.Session()
        self.session.mount(
            self.site,
            self.gateway
        )

        self._is_setup = True

    def get(self, url, params={}, fail_count=0):
        full_url = url + '?' + urllib.parse.urlencode(params)
        if len(url) > 1000:
            raise ValueError('URL too long')
        try:
            response = self.session.get(
                full_url
            )

            if self.site == 'https://api-finder.eircode.ie':
                if response.json().get('error', {}).get('code', None) == 403:
                    raise Exception(response.json()['error']['text'])
            return response
        except:
            if fail_count > 5:
                raise Exception('Retried too many times')

            logger.error('Proxy error')
            if random.random() < 0.05:
                logger.info('Resetting proxy')
                self.shutdown()
                self.setup(force=True)
            return self.get(url, params=params, fail_count=fail_count + 1)

    def shutdown(self):
        self.gateway.shutdown()


proxy = Proxy(skip_setup=True)
