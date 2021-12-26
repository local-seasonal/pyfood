
</br>

<p align="center">
  <img height="80px" src="docs/img/pyfood-logo.svg" alt="pyfood_logo">
</p>

</br>

<p align="center">
  <!-- Tests
  <a href="https://github.com/username/repo/actions/workflows/unit-tests.yml">
    <img src="https://github.com/username/repo/actions/workflows/unit-tests.yml/badge.svg" alt="tests">
  </a>
   -->
  <!-- Code coverage 
  <a href="https://codecov.io/gh/username/repo">
    <img src="https://codecov.io/gh/username/repo/branch/main/graph/badge.svg?token=token"/>
  </a>
  -->
  <!-- Documentation
  <a href="https://readthedocs.org/">
    <img src="https://img.shields.io/website?label=docs&style=flat-square&url=website_url" alt="documentation">
  </a>
  -->
  </a>
  <!-- PyPI -->
  <a href="https://pypi.org/project/pyfood">
    <img src="https://img.shields.io/pypi/v/pyfood.svg?label=release&color=blue&style=flat-square" alt="pypi">
  </a>
  <!-- License -->
  <a href="http://creativecommons.org/licenses/by/4.0/">
    <img src="https://img.shields.io/badge/License-CC--BY--4.0-blue.svg?style=flat-square" alt="creative_commons_license">
  </a>
</p>

</br>

<p align="center">
  Pyfood is a simple Python package to process food, in different languages. Pyfood's ambition is to be the go-to library to deal with food, recipes, online menus or cookbooks.
</p>

## Installation 

Pyfood is intended to work with **Python 3.6 or above**. Installation can be done with `pip`:

```sh
pip install pyfood
```

## Quickstart

At the core of Pyfood is the concept of a ``shelf`` embedded in a given ``region``, a certain ``month_id`` and optionally a ``source`` language.
You can load a shelf embedded in France in January with the following Python snippet:

```python
from pyfood.utils import Shelf
shelf = Shelf(region='France', month_id=0)
```

Pyfood currently works in the following regions: 
- **Canada** 🇨🇦
- **EU** 🇪🇺 (Europe, default)
- **France** 🇫🇷
- **Germany** 🇩🇪
- **Israel** 🇮🇱 
- **Italy** 🇮🇹
- **Japan** 🇯🇵
- **Portugal** 🇵🇹
- **Senegal** 🇸🇳
- **Spain** 🇪🇸
- **United Kingdom** 🇬🇧

### 🍐 Label baskets or recipes

Pyfood can help automatically extract and label a list of ingredients, e.g., from a basket of food, a recipe, a menu, a cookbook or a website, with attributes/categories (e.g., fruits, vegetables) and labels (e.g., vegetarian, vegan, nutrition, seasonality), in a few lines of code:

```python
results = shelf.process_ingredients(['apple','kiwi','sugar'])
results['labels'] # vegetarian, vegan, nutrition, seasonality
```

### 🍋 Translate ingredients
Pyfood comes with a vocabulary of more than 600 ingredients and synonymes, in multiple languages, and makes it easy to work with recipes in different languages or translate ingredients from a language to another one:

```python
results = shelf.process_ingredients(['apple','kiwi','sugar'], lang_dest='FR')
results['food_list'] # pomme, kiwi, sucre
```

Pyfood currently supports the following languages:
- **DE** (German)
- **EN** (English)
- **ES** (Spanish)
- **FR** (French)
- **IT** (Italian)
- **PT** (Portuguese)
- **UN** (Universal, default)

### 🍓 What's in season?

Finally, Pyfood can also be used to simply query what [fruits](https://www.local-seasonal.org/en/on-the-menu?name=Fruits) or [vegetables](https://www.local-seasonal.org/en/on-the-menu?name=Vegetables) are in season:

```python
fruits_in_season = shelf.get_seasonal_food(key='001')
vegetables_in_season = shelf.get_seasonal_food(key='002')
```

## Credits

📊 [CIQUAL ANSES](https://ciqual.anses.fr/) <br>
📷 [Pexels](https://www.pexels.com/) <br>
📷 [Unsplash](https://unsplash.com/)

## Useful links

- [Documentation]() See `docs/build/index.html`
- [Issue tracker](https://github.com/local-seasonal/pyfood/issues)
- [Package releases](https://pypi.org/project/pyfood/#history)

## License

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a> by [Local Seasonal](https://www.local-seasonal.org/)
