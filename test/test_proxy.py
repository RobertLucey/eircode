from unittest import TestCase, skip

from eircode.proxy import Proxy


class ProxyTest(TestCase):

    @skip('if no aws creds just skip')
    def test_proxy(self):
        proxy = Proxy(site='https://api.ipify.org')

        first_request = proxy.get('https://api.ipify.org')
        first = first_request.text

        proxy.shutdown()
        proxy.setup(force=True)

        second_request = proxy.get('https://api.ipify.org')
        second = second_request.text

        self.assertNotEqual(first, second)
