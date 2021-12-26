Pyfood API
==========

Pyfood is a simple Python package to process food, in different languages. At the core of Pyfood is the concept of a ``shelf`` embedded in a given ``region``, a certain ``month_id`` and optionally a ``source`` language.
You can load a shelf embedded in France in January with the following Python snippet:

.. code-block:: python
    
    from pyfood.utils import Shelf
    shelf = Shelf(region='France', month_id=0) 

Pyfood currently works with the following regions: **France** 🇫🇷, **Italy** 🇮🇹, **Spain** 🇪🇸, **Portugal** 🇵🇹, **Germany** 🇩🇪, **EU** 🇪🇺 (Europe, default), **United Kingdom** 🇬🇧, **Canada** 🇨🇦, **Japan** 🇯🇵, **Israel** 🇮🇱 and **Senegal** 🇸🇳. It supports the following languages **EN** (English), **FR** (French), **ES** (Spanish), **IT** (Italian), **DE** (German), **PT** (Portuguese) and **UN** (Universal, default)

Pyfood shelf
-------------

.. autoclass:: pyfood.utils.Shelf
	:members: __init__, get_seasonal_food, get_food_info, text2food, process_ingredients
