Eircode
=======

Tool to get eircodes from an address

Installation
------------

`pip install eircode`

Usage
-----

```python
>>> from eircode.address import Address
>>> address = Address('4 MAIN STREET, Co. CLARE')
>>> address.serialize()
{'display_name': '4 MAIN STREET, NEWMARKET-ON-FERGUS, Co. CLARE',
 'eircode': {'county': 'Clare',
             'eircode': 'V95K2W0',
             'routing_key': 'V95',
             'towns': ['Miltown Malbay', 'Ennis', 'Kildysart'],
             'unique_identifier': 'K2W0'},
 'link': None}
```
