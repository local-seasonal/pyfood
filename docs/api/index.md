Pyfood API
==========

Pyfood is a simple Python package to process food, in different languages. At the core of Pyfood is the concept of a ``shelf`` embedded in a given ``region``, a certain ``month_id`` and optionally a ``source`` language.
You can load a shelf embedded in France in January with the following Python snippet:

.. code-block:: python
    
    from pyfood.utils import Shelf
    shelf = Shelf(region='France', month_id=0) 

Pyfood supports the following language by default ``UN`` (**Universal**), which includes ``DE`` (German), ``EN`` (English), ``ES`` (Spanish). ``FR`` (French), ``IT`` (Italian), ``PT`` (Portuguese). Pyfood works in the following region by default ``EU`` (**Europe**), which includes ``France``, ``Germany``, ``Italy``, ``Portugal``, ``Spain``, ``United Kingdom``. Support for ``Canada``, ``Israel``, ``Japan`` and ``Senegal`` is also provided.

Pyfood Shelf
-------------

.. autoclass:: pyfood.utils.Shelf
	:members: __init__, get_seasonal_food, get_food_info, text2food, process_ingredients
