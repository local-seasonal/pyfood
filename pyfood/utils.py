import re
import json
import unidecode
import urllib.parse
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix, load_npz
from typing import List, Tuple, Dict, Optional


import os

prefix = os.path.dirname(os.path.abspath(__file__))


with open(os.path.join(prefix, "assets", "nutri", "units.json"), "r") as fp:
    units = json.load(fp)

with open(os.path.join(prefix, "assets", "nutri", "nutrimap.json"), "r") as fp:
    nutrimap = json.load(fp)

with open(os.path.join(prefix, "assets", "nutri", "vnr.json"), "r") as fp:
    vnr = json.load(fp)


def lists2object(
    foodnames: List[str], quantities: List[str], unit_list: List[str], taxons: List[str]
) -> List[Dict]:
    """Returns a list of dict from multiple lists."""
    output = []
    for u, v, w, x in zip(foodnames, quantities, unit_list, taxons):
        output.append({"foodname": u, "quantity": v, "unit": w, "taxon": x})
    return output


def str2float(string: str) -> float:
    """Converts a string to a float."""
    try:
        if "/" not in string:
            return float(string)
        else:
            return float(string.split("/")[0]) / float(string.split("/")[1])
    except:
        return 1.0


def str2ngrams(string: str) -> List[str]:
    """Converts a string to a list of ngrams (monogram, bigram, trigram)."""
    ngrams = string.split()  # monograms
    token_list = string.split()
    if len(token_list) > 2:
        ngrams += [
            w1 + " " + w2 + " " + w3
            for w1, w2, w3 in zip(token_list[:-2], token_list[1:-1], token_list[2:])
        ]  # trigrams
    if len(token_list) > 1:
        ngrams += [
            w1 + " " + w2 for w1, w2 in zip(token_list[:-1], token_list[1:])
        ]  # bigrams
    return ngrams


class Shelf(object):
    """Pyfood shelf embedded in a given region, month_id and optionally source language"""

    def __init__(self, region: str = "EU", lang_source: str = "un", month_id: int = 0):
        """Instantiates a shelf from a context (region, lang_source, month_id)."""
        self.region, self.lang_source, self.month_id = (
            region,
            lang_source.lower(),
            month_id,
        )

        with open(os.path.join(prefix, "assets", "vocab", "mapping.json"), "r") as fp:
            mapping = json.load(fp)  # food univeral mapping (f2id, id2f)
            self.mapping = mapping[
                self.lang_source
            ]  # load session's language for basket of food (BOW) representation

        with open(os.path.join(prefix, "assets", "vocab", "feats.json"), "r") as fp:
            self.feats = json.load(
                fp
            )  # food attributes {food_id: {'taxon': , 'fr': , 'es': , 'en': , 'default_weight': , 'default_density': , 'benefits/diet': , nutri...}}
            self.n_ingredients = len(self.feats)  # total number of ingredients

        self.seasonal_matrix = load_npz(
            os.path.join(
                prefix, "assets", "seasons", "sparse_seasons_{}.npz".format(region)
            )
        )  # domain expert knowledge (n_seasons, n_food) varies by 'regions'
        self.seasonal_vector = np.ravel(
            self.seasonal_matrix[self.month_id].toarray()
        )  # local and seasonal ingredients   ##### map2producers
        self.tfidf = None  # language model (ngrams2vec)
        self.model = None  # RBM model (revise)

    def get_seasonal_food(self, key: str = "001") -> List[str]:
        """
        Returns what food is in season

        Parameters
        ----------
        key : str
            taxon code (fruits: 001, vegetables: 002, ..., mushrooms: 005)

        Returns
        ----------
        list
            seasonal_food: Food in seasons in self.region, self.month_id and self.lang_source
        """

        seasonal_food = []
        for fid in np.argwhere(self.seasonal_vector > 0.0):
            feats = self.feats[str(float(fid))]
            foodname = feats[self.lang_source]
            taxon = feats["taxon"]
            if taxon.startswith(key):
                seasonal_food.append(foodname.capitalize())
        seasonal_food = np.sort(seasonal_food)
        return list(seasonal_food)

    def get_urls(self, food_list: List[str]) -> List[str]:
        return [
            self.feats[str(self.mapping["f2id"][foodname.lower()])]["url"]
            for foodname in food_list
        ]

    def get_nutri(self, food_list: List[str], category: str = "minerals") -> List:
        nutri_list = []
        for foodname in food_list:
            # fid = str(self.mapping['f2id'][foodname.lower()])
            # if category == 'minerals':
            #    nutri_tags = self.feats[fid]['top_Minerals']
            # else:
            #    nutri_tags = self.feats[fid]['top_Vitamins']
            # nutri_list.append(nutri_tags)
            nutri_list.append([])
        return nutri_list

    def load_tfidf(self):
        """Loads self.lang_source language model."""
        if self.tfidf is None:
            self.tfidf = pickle.load(
                open(
                    os.path.join(
                        prefix,
                        "assets",
                        "vocab",
                        "{}/tfidf_{}.pickle".format(self.lang_source, self.lang_source),
                    ),
                    "rb",
                )
            )  # ngram vectorizer for food names
            self.ngrams = pickle.load(
                open(
                    os.path.join(
                        prefix,
                        "assets",
                        "vocab",
                        "{}/ngrams_{}.pickle".format(
                            self.lang_source, self.lang_source
                        ),
                    ),
                    "rb",
                )
            )

    def get_food_info(self, food_name: str) -> Tuple:
        """
        Returns food id, taxon and seasonality.

        Parameters
        ----------
        food_name : str
            Food name in self.lang_source

        Returns
        ----------
        food_name : str
            Food name in self.lang_source
        fid : float
            Food id in self.lang_source
        taxon : str
            Food taxon (fruits: 001, vegetables: 002, ..., mushrooms: 005)
        score : float
            Food score in self.region and self.month_id
        """

        fid = self.mapping["f2id"][
            food_name
        ]  # ref id, for example: Reine Claude --> Prune
        taxon = self.feats[str(fid)]["taxon"]
        score = self.seasonal_vector[int(fid)]
        return food_name, fid, taxon, score

    def text2food(self, food_name: str = "apple", threshold: float = 0.0) -> Tuple:
        """
        Retrieves ingredient from vocabulary using `tdfidf` and `cosine_similarity`. Returns food id, taxon and seasonality.

        Parameters
        ----------
        food_name : str
            (Noisy) food name in self.lang_source

        Returns
        ----------
        food_name : str
            Food name in self.lang_source
        fid : float
            Food id in self.lang_source
        taxon : str
            Food taxon (fruits: 001, vegetables: 002, ..., mushrooms: 005)
        score : float
            Food score in self.region and self.month_id
        """

        if food_name in self.mapping["f2id"]:
            food_name, fid, taxon, score = self.get_food_info(food_name=food_name)
            return food_name, fid, taxon, score

        food_name = urllib.parse.unquote(
            food_name
        )  # replace %xx escapes by their single-character equivalent (utf-8 encoding)
        food_name = (
            re.sub(r"\(.*\)", "", food_name).lower().strip()
        )  # remove parenthesis, lower case and strip string
        if food_name in self.mapping["f2id"]:
            food_name, fid, taxon, score = self.get_food_info(food_name=food_name)
            return food_name, fid, taxon, score

        food_name_az = unidecode.unidecode(
            food_name
        )  # convert unicode with accents to unaccented_string
        food_name_az = re.sub(
            "[^a-zA-Z]+", " ", food_name_az
        ).strip()  # replace apostrophees, non alpha characters by spaces and strip string
        if food_name_az in self.mapping["f2id"]:
            food_name, fid, taxon, score = self.get_food_info(food_name=food_name_az)
            return food_name, fid, taxon, score

        self.load_tfidf()
        candidates = str2ngrams(food_name) + str2ngrams(food_name_az)  # list of ngrams
        candidates = list(set(candidates))  # remove duplicate ngrams
        penalty = np.array([[len(c) / len(food_name)] for c in candidates])
        affinity = penalty * cosine_similarity(
            self.tfidf.transform(candidates), self.ngrams, dense_output=True
        )  # (len(candidates), n_ingredients)
        neighbors_id = np.argmax(affinity, axis=1)
        values = np.array([affinity[i][j] for i, j in enumerate(neighbors_id)])
        row = np.argmax(values)
        nearest_neighbor_id = neighbors_id[row]
        nearest_neighbor_similarity = values[row]
        if nearest_neighbor_similarity > threshold:
            food_name = self.mapping["id2f"][str(float(nearest_neighbor_id))]
            food_name, fid, taxon, score = self.get_food_info(food_name=food_name)
            return food_name, fid, taxon, score
        else:
            return food_name, None, None, None

    def convert2g(self, fid: float, qty: float, unit: str) -> float:
        """Converts a food id, quantity and unit in grams.

        Parameters
        ----------
        fid : float
            Food id
        qty : float
            Quantity
        unit : str
            Unit

        Returns
        ----------
        weight: float
            Quantity in grams
        """

        unit = unit.lower()
        if unit == "default":
            return qty * self.feats[str(fid)]["default_weight"]  # convert to g
        if unit in units["masse"]:
            return qty * float(units["masse"][unit])
        if unit in units["volume"]:
            return qty * float(units["volume"][unit]) * self.feats[str(fid)]["density"]
        if unit in units["misc"]:
            return (
                qty
                * float(units["misc"][unit])
                * self.feats[str(fid)]["default_weight"]
            )
        return qty * self.feats[str(fid)]["default_weight"]

    def NER(
        self,
        food_list: List[str],
        qty_list: Optional[List[str]],
        unit_list: Optional[List[str]],
        lang_dest: Optional[str],
        filter_HS: bool = True,
    ) -> Tuple:
        """Named Entity Recognition on a food (+ optionally quantity and unit) list.

        Parameters
        ----------
        food_list : list
            (Noisy) list of food name in self.lang_source
        qty_list : list
            List of quantities
        unit_list : list
            List of units
        lang_dest : str
            Target language (default self.lang_source)

        Returns
        ----------
        recipe_vector : np.array(self.n_ingredients,1)
            Vectorized basket of food
        foodnames : list
            Denoised food list in self.lang_source
        qties : list
            List of quantities (str)
        units : list
            List of units (str)
        taxons : list
            List of taxons
        HS : list
            List of food out of season
        """

        if lang_dest is None:
            lang_dest = self.lang_source
        else:
            lang_dest = lang_dest.lower()
        if qty_list is None:
            qty_list = ["100"] * len(food_list)
        if unit_list is None:
            unit_list = ["g"] * len(food_list)

        recipe_vector = np.zeros(
            (self.n_ingredients, 1)
        )  # basket of food (n_ingredients,1)
        foodnames, qties, units, taxons = (
            [],
            [],
            [],
            [],
        )  # extracted entity (length < food_list)
        HS, HS_id = [], []  # hors saison

        for (food_, qty_, unit_) in zip(food_list, qty_list, unit_list):  # ingredients
            food_, fid, taxon, score = self.text2food(food_name=food_)
            if fid is not None:  # food_ is in food vocab
                if lang_dest != self.lang_source:
                    food_ = self.feats[str(fid)][lang_dest]  # translate food name
                qty_ = str2float(qty_)
                weight = self.convert2g(fid, qty_, unit_)  # convert to g
                recipe_vector[int(fid)] += weight  # quantity in g
                if filter_HS and (
                    score < 0.5 or taxon.startswith("21")
                ):  # seasonality threshold below 0.5 or non vege ingredient (i.e. fish, meat, egg, seafood)
                    HS.append(food_)
                    HS_id.append(fid)
                else:
                    qties.append(qty_)
                    units.append(unit_)
                    taxons.append(taxon)
                    foodnames.append(food_)

        return recipe_vector, foodnames, qties, units, taxons, HS, HS_id

    def process_ingredients(
        self,
        food_list: List[str],
        qty_list: Optional[List[str]],
        unit_list: Optional[List[str]],
        lang_dest: Optional[str],
        revisit: bool = False,
        infer_nutri: bool = False,
        serving: int = 1,
    ):
        """Labels a list of ingredients, e.g., from a recipe or a basket of food, and saves attributes / labels in self.tags

        Parameters
        ----------
        food_list : list
            List of food name in self.lang_source
        qty_list : list
            List of quantities or None
        unit_list : list
            List of units or None
        lang_dest : str
            Target language, default self.lang_source
        revisit : bool
            Infer Recipe2BetterRecipe, default False
        infer_nutri : bool
            Infer nutrition scores, default False
        serving : int
            Number of portions, default 1.

        Returns
        -------
        tags: dict
            Extracted ingredients (ingredients_by_taxon, HS, revisited), predicted nutrition (allergies, energy, macro, minerals, vitamines) and labels (vege, vegan, seasonality)
        """

        # read recipe
        my_recipe_vector, foodnames, qties, unit_list, taxons, HS, HS_id = self.NER(
            food_list=food_list,
            qty_list=qty_list,
            unit_list=unit_list,
            lang_dest=lang_dest,
        )  # map ingredients to basket of food
        self.tags = {}  # init tags
        self.tags["ingredients"] = lists2object(
            foodnames, qties, unit_list, taxons
        )  # seasonal and vege ingedients
        self.tags["HS"] = HS  # rest of ingredients

        self.tags[
            "ingredients_by_taxon"
        ] = {}  # dict of list, e.g. 001: [pomme, poire], 101: [sel]
        for foodname, taxon in zip(foodnames, taxons):
            if taxon not in self.tags["ingredients_by_taxon"]:
                self.tags["ingredients_by_taxon"][taxon] = [foodname]
            else:
                self.tags["ingredients_by_taxon"][taxon].append(foodname)
        self.tags["ingredients_by_taxon"] = [
            self.tags["ingredients_by_taxon"][taxon]
            for taxon in np.sort(np.unique(taxons))
        ]  # list of list, e.g. [ [pomme, poire], [sel] ]

        # infer seasonality
        if my_recipe_vector.sum() == 0:
            self.tags["labels"] = {
                "vegan": False,
                "vege": False,
                "seasonality": {"region": self.region, "score": 0, "best_now": False},
            }
            self.tags["revisited"] = []
            if infer_nutri == True:
                self.tags["nutri"] = {
                    "Allergies": {},
                    "Energy": {},
                    "Macro": {},
                    "Minerals": {},
                    "Vitamines": {},
                }

        else:
            my_recipe_vector /= (
                my_recipe_vector.sum()
            )  # normalize ingredients (proportions) for seasonality
            my_seasons_vector = (
                self.seasonal_matrix * csr_matrix(my_recipe_vector)
            ).toarray()  # infer seasonality from seasonal ingredients: (n_seasons,n_ingredients) * (n_ingredients,1) = (n_seasons,1)
            seasonality = {
                "city": self.region,
                "score": int(100 * my_seasons_vector[self.month_id][0]),
                "best_now": len(HS) == 0,
            }

            # infer labels
            is_vege = (
                len(
                    [
                        1
                        for fid in HS_id
                        if self.feats[str(fid)]["taxon"].startswith("21")
                    ]
                )
                == 0
            )  # Vegetarian label
            is_vegan = (
                is_vege and len([1 for taxon in taxons if taxon.startswith("2")]) == 0
            )  # Vegan label (check no diary and cheese)
            self.tags["labels"] = {
                "vegan": is_vegan,
                "vege": is_vege,
                "seasonality": seasonality,
            }

            # revisit recipe
            revisited = []
            # if revisit==True and (self.lang_source==lang_dest or lang_dest==None):
            #    # revisited = self.sample(my_recipe_vector, nsamples=len(HS)) #####
            #    revisited = []
            #    for hs, hs_id in zip(HS, HS_id): # taxon constraint
            #        hs_taxon = self.feats[str(hs_id)]['taxon']
            #        ideas = self.harmonize(food=hs, nsamples=4)
            #        for idea in ideas:
            #            revisited.append(idea)
            self.tags["revisited"] = list(set(revisited))

            ##### Infer nutriscores [HEALTH]
            # infer nutriscores and VNR
            if infer_nutri == True:
                nutrition = {"Energy": {}, "Macro": {}, "Minerals": {}, "Vitamins": {}}
                nutriscores = load_npz(
                    os.path.join(prefix, "assets", "nutri", "sparse_nutriscores.npz")
                )  # load nutriscores matrix
                my_nutri_vector = (nutriscores * csr_matrix(my_recipe_vector)).toarray()
                my_nutri_vector = my_nutri_vector / float(serving)
                for c in ["Energy", "Macro", "Minerals", "Vitamins"]:
                    for nutri_name, nutri_id in nutrimap[c].items():
                        composcore = (
                            100 * float(my_nutri_vector[nutri_id]) / vnr[c][nutri_name]
                        )  # infer kCal (energy), macro scores, minerals scores and vitamines scores (% VNR) + Allergies (0 ou 1)
                        if composcore > 0:
                            nutrition[c][nutri_name] = composcore
                self.tags["nutri"] = nutrition

            return self.tags
