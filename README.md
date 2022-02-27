Eircode
=======

Tool to get eircodes from an address. Optional proxy to avoid rate limiting.

Installation
------------

`pip install eircode`

Usage
-----

```python
>>> from eircode.address import Address
>>> address = Address('4 MAIN STREET, Co. CLARE', proxy=False)
>>> address.serialize()
{'display_name': '4 MAIN STREET, NEWMARKET-ON-FERGUS, Co. CLARE',
 'eircode': {'county': 'Clare',
             'eircode': 'V95K2W0',
             'routing_key': 'V95',
             'towns': ['Miltown Malbay', 'Ennis', 'Kildysart'],
             'unique_identifier': 'K2W0'},
 'link': None}
```

Using a proxy
-------------

You need to set up an APIGateway API named 'restapis' in eu-west-1. Then add a GET method to it. Once you have auth details in ~/.aws and they have access to the api it should just work.
