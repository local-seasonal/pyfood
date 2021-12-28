Quickstart
==========


Installation
------------

Pyfood is a simple Python package to process food, in different languages

.. code-block:: console

	$ pip install pyfood

will install Pyfood alongside all the other libraries that you will need to run it.

Examples
--------

At the core of Pyfood is the concept of a ``shelf`` embedded in a given ``region``, a certain ``month_id`` and optionally a ``source`` language.
You can load a shelf embedded in France in January with the following Python snippet:

.. code-block:: python
    
    from pyfood.utils import Shelf
    shelf = Shelf(region='France', month_id=0)


Pyfood works in the following region by default ``EU`` (**Europe**), which includes ``France``, ``Germany``, ``Italy``, ``Portugal``, ``Spain``, ``United Kingdom``. Support for ``Canada``, ``Israel``, ``Japan`` and ``Senegal`` is also provided.
In a few lines of code, Pyfood can help automatically **extract, translate, label** a list of ingredients, e.g., from a basket of food, a recipe, a menu, a cookbook or a webapp with multiple labels, e.g., vegetarian, vegan, nutrition, seasonality.

.. code-block:: python

    results = shelf.process_ingredients(['apple','kiwi','sugar'])
    results['labels'] # vegetarian, vegan, nutrition, seasonality

Pyfood comes with a vocabulary of more than 600 ingredients and synonymes, in multiple languages, and makes it easy to work with recipes in different languages or translate ingredients from a language to another one.

.. code-block:: python

    results = shelf.process_ingredients(['apple','kiwi','sugar'], lang_dest='FR')
    results['ingredients_by_taxon'] # pomme, kiwi, sucre

Pyfood supports the following language by default ``UN`` (**Universal**), which includes ``DE`` (German), ``EN`` (English), ``ES`` (Spanish). ``FR`` (French), ``IT`` (Italian), ``PT`` (Portuguese). Finally, Pyfood can also be used to simply query what fruits or vegetables are in season, which depends on the ``region`` and ``month_id`` selected.

.. code-block:: python

    fruits_in_season = shelf.get_seasonal_food(key='001')
    vegetables_in_season = shelf.get_seasonal_food(key='002')
