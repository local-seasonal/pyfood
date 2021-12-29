Pyfood Assets
=============

Food is a universal language and Pyfood is a simple Python package to process food. It comes with assets described below to automatically extract, tag or translate baskets of food, recipes or cookbooks with labels, e.g. vegetarian, vegan, nutrition or seasonality.

Important note: Pyfood is still work in progress. Therefore, some fields below might be empty and need further work. You're welcome to `open an issue on Github <https://github.com/local-seasonal/pyfood/issues>`_ or reach out directly to the project contributors for any question, comment or feedback. Thank you! 🙏

Vocabulary
----------

Similar to English, French or Music, `food as a language <https://web.stanford.edu/~jurafsky/thelanguageoffood.html>`_ comes with its own alphabet, vocabulary and grammar.
The grammar deals with composition or how to make a soup out of ingredients, step by step. It's pretty well accessible and understood. 
The vocabulary is about the ingredients themselves. What is a strawberry? Where and when does it grow? What benefits does it have?

Each ingredient in Pyfood's vocabulary is unique and has its own attributes (names, synonymes, nutrition, seasonality, etc) which varies by ``region`` and ``month_id``.
See below for an example in ``assets/vocab/feats.json``.

.. code-block:: python
    
    "0.0": {
        "taxon": "001",
        "default_weight": 10,
        "density": 1.0,
        "allergen": "None",
        "url": "https://images.pexels.com/photos/...",
        "CIQUAL_ref": "Abricot, denoyaute, cru",
        "kCal": 42.6,
        "macro": "Protein:1.01, Glucides:7.14, AcidesGrasSatures:0.024, AcidesOrganiques:1.4, Sucre:6.57, Fibres:1.8, Lipides:0.35",
        "minerals": "Ca:16.1, Cu:0.082, Fe:0.19, I:0.37, Mg:9.94, Mn:0.071, P:22.5, K:229, Se:10, Na:1.11, Zn:0.14",
        "vitamins": "Beta:1090, E:0.89, C:10, B1:0.03, B2:0.04, B3:0.6, B5:0.24, B6:0.054, B9:9",
        "un": "abricot",
        "fr": "abricot",
        "es": "albaricoque",
        "en": "apricot",
        "it": "albicocca",
        "pt": "alperce",
        "de": "aprikose",
        "zh": "\u674f",
    },

Taxon is a code to identify which family an ingredient belongs to and can be used for example to predict if a recipe or basket of food is vegan or vegetarian.

.. list-table:: Taxon used
   :widths: 25 25 50
   :header-rows: 1

   * - 0xx (seasonal)
     - 1xx (non seasonal)
     - 2xx (non vegan)
   * - 001: ``Fruits``
     - 101: ``Spice``
     - 201: ``Diary``
   * - 002: ``Vegetables``
     - 102: ``Helpers``
     - 202: ``Cheese``
   * - 003: ``Leguminous``
     - 103: ``Cereals``
     - 203: ``Eggs``
   * - 004: ``Mushrooms``
     - 104: ``Pasta``
     - 
   * - 005: ``Nuts``
     - 105: ``Bread``
     - 211: ``Fish``
   * - 006: ``Algae``
     - 106: ``Plant based diary``
     - 212: ``Poultry``
   * - 007: ``Plants``
     - 107: ``Sugary``
     - 213: ``Sea food``
   * - 008: ``Herbs``
     - 110: ``Alcohol``
     - 214: ``Meat``

Nutrition
---------

More than 90% of Pyfood ingredients are mapped to a nutritional database `CIQUAL ANSES <https://ciqual.anses.fr/>`_ which contains the following information for each ingredient: ``kCal``, ``macro``, ``minerals``, ``vitamins``. In addition, we have added an attribute ``allergen`` for each ingredient and recommended nutritional values in ``assets/nutri/vnr.json``.


.. list-table:: Details about the macro, minerals and vitamins subfields
   :widths: 25 25 50
   :header-rows: 1

   * - macro
     - minerals
     - vitamins
   * - ``Protein``
     - ``Ca``
     - ``A``
   * - ``Lipides``
     - ``Cu``
     - ``B1``
   * - ``AcidesGrasSatures``
     - ``Fe``
     - ``B2``
   * - ``AcidesOrganiques``
     - ``I``
     - ``B3``
   * - ``Glucides``
     - ``Mg``
     - ``B5``
   * - ``Sucre``
     - ``Mn``
     - ``B6``
   * - ``Fibres``
     - ``P``
     - ``B9``
   * - 
     - ``K``
     - ``C``
   * - 
     - ``Se``
     - ``E``
   * - 
     - ``Na``
     - ``Beta``
   * - 
     - ``Zn``
     - 

Seasonality
-----------

What ingredient is in season (cf taxon code **0xx**) is written in text files under ``assets/seasons/input/`` (12 rows per ``region``, each corresponding to a ``month_id``)
This information is saved as sparse matrices for efficient storage and calculations.
