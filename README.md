Eircode
=======

Tool to get eircodes from an addresses / addresses from eircodes. Optional proxy to avoid rate limiting.

Also includes tools to parse eircodes.

Installation
------------

`pip install eircode`

Usage
-----

```python
>>> from eircode.address import Address
>>> address = Address('4 MAIN STREET, Co. CLARE', proxy=False, reverse=False)
>>> address.serialize()
{'display_name': '4 MAIN STREET, NEWMARKET-ON-FERGUS, Co. CLARE',
 'eircode': {'county': 'Clare',
             'eircode': 'V95K2W0',
             'routing_key': 'V95',
             'towns': ['Miltown Malbay', 'Ennis', 'Kildysart'],
             'unique_identifier': 'K2W0'},
 'link': None}
>>> address = Address('V95K2W0', proxy=False, reverse=True)
>>> address.serialize()
{'display_name': '4 MAIN STREET, NEWMARKET-ON-FERGUS, ENNIS, CO. CLARE',
 'eircode': {'county': 'Clare',
             'eircode': 'V95K2W0',
             'routing_key': 'V95',
             'towns': ['Miltown Malbay', 'Ennis', 'Kildysart'],
             'unique_identifier': 'K2W0'},
 'link': None}
>>> from eircode.eircode import Eircode
>>> Eircode('A41AAAA').serialize()
{'routing_key': 'A41',
 'unique_identifier': 'AAAA',
 'eircode': 'A41AAAA',
 'county': 'Dublin',
 'towns': ['Ballyboughal']}
```
