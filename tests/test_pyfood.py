''' Test pyfood (requirements, assets, functionalities)'''

import os
import sys
sys.path.insert(0,os.path.dirname('pyfood/'))


def test_imports():
    ''' Test imports and dependencies'''
    import re
    import json
    import pickle
    import time
    import numpy as np
    import pandas as pd
    import sklearn
    import scipy

def test_builder():
    ''' Test builder for assets (vocab,  nutri, seasons, recipes, world)'''
    from build_assets import build
    build(assets_paths='pyfood/assets', verbose=1)

def test_vocab(assets_paths='pyfood/assets'):
    ''' Test assets (1)'''
    import pandas as pd
    import json

    # load vocab from csv: fr, en, es, it + taxons
    df = pd.read_csv(os.path.join(assets_paths,'vocab/vocab.csv'))
    assert len(df)>500 # number of unique ingredients

    # load food mapping.json
    with open(os.path.join(assets_paths,'vocab/mapping.json'), 'r') as fp:
        mapping = json.load(fp)
    assert 'es' in mapping.keys() and 'fr' in mapping.keys() and 'en' in mapping.keys() and 'it' in mapping.keys()
    assert len(mapping['fr']['id2f']) >= len(mapping['fr']['f2id']) # synonyms id2f > f2id
    assert len(mapping['en']['id2f']) >= len(mapping['en']['f2id'])
    assert len(mapping['es']['id2f']) >= len(mapping['es']['f2id'])
    assert len(mapping['it']['id2f']) >= len(mapping['it']['f2id'])
    assert len(mapping['fr']['f2id']) >= 500
    assert len(mapping['en']['f2id']) >= 500
    assert len(mapping['es']['f2id']) >= 500
    assert len(mapping['it']['f2id']) >= 500

    # load food feats.json
    with open(os.path.join(assets_paths,'vocab/feats.json'), 'r') as fp:
        feats = json.load(fp)
    assert len(df) == len(feats)
    assert 'taxon' in feats['0.0'] and 'fr' in feats['0.0'] and 'es' in feats['0.0'] and 'en' in feats['0.0'] and 'it' in feats['0.0']
    assert 'default_weight' in feats['0.0'] and 'density' in feats['0.0'] and 'allergen' in feats['0.0'] and 'url' in feats['0.0']
    assert 'default_weight' in feats['0.0'] and 'density' in feats['0.0'] and 'allergen' in feats['0.0'] and 'url' in feats['0.0']
    assert 'CIQUAL_ref' in feats['0.0'] and 'kCal' in feats['0.0'] and 'macro' in feats['0.0'] and 'minerals' in feats['0.0'] and 'vitamins' in feats['0.0'] # from CIQUAL

def test_charagram(assets_paths='pyfood/assets'):
    ''' Test assets (2)'''
    import pandas as pd
    import json
    import pickle

    # load food mapping.json
    with open(os.path.join(assets_paths,'vocab/mapping.json'), 'r') as fp:
        mapping = json.load(fp)

    # load charagram language model
    for lang in ['fr', 'en', 'es', 'it']:
        tfidf = pickle.load(open(os.path.join(assets_paths,'vocab/{}/tfidf_{}.pickle'.format(lang, lang)), "rb")) # ngram vectorizer for food names
        ngrams = pickle.load(open(os.path.join(assets_paths,'vocab/{}/ngrams_{}.pickle'.format(lang, lang)), "rb"))
        assert ngrams.shape[0]>=len(mapping) # synonymes
        
def test_nutriscores(assets_paths='pyfood/assets'):
    ''' Test assets (3)'''
    import json
    from scipy.sparse import load_npz

    with open(os.path.join(assets_paths, 'nutri/nutrimap.json'), 'r') as fp:
        nutrimap = json.load(fp)
        nutrikeys = [kk for d in nutrimap.values() for kk in d.keys()]
    assert 'Energy' in nutrimap and 'Macro' in nutrimap and 'Minerals' in nutrimap and 'Vitamins' in nutrimap

    with open(os.path.join(assets_paths, 'vocab/feats.json'), 'r') as fp:
        feats = json.load(fp)

    dense_scores = load_npz(os.path.join(assets_paths,'nutri/sparse_nutriscores.npz')).toarray() # nutri info from CIQUAL
    assert dense_scores.shape[0] == len(nutrikeys) # n feats
    assert dense_scores.shape[1] == len(feats) # n ingredients

def test_seasonality(assets_paths='pyfood/assets'):
    ''' Test assets (4)'''
    import json
    from scipy.sparse import load_npz

    with open(os.path.join(assets_paths,'vocab/feats.json'), 'r') as fp:
        feats = json.load(fp)

    ### load sparse matrix
    for region in ['Japan','France','Spain','Senegal','Canada','United Kingdom']:
        sparse_seasonality = load_npz(os.path.join(assets_paths,'seasons/sparse_seasons_{}.npz'.format(region))) #  csr_matrix((data, (row, col)), shape=(12, n_ingredients), dtype=np.float) # ingredients <-> seasons 
        fail_months, fail_food = (sparse_seasonality>1.).nonzero()
        assert len([feats[str(float(wid))]['fr'] for wid in set(fail_food)]) == 0
        assert len(fail_food) == 0

def test_text2food():
    ''' Test shelf class'''

    # load shelf from region, lang_source and month_id
    from utils import Shelf
    shelf = Shelf()
    assert shelf.region == "EU" # default region (European Union)
    assert shelf.lang_source == 'un' # default language (universal)

    foodname,fid,taxon,score = shelf.text2food(food_name="Tomates cerise", threshold=0.)
    assert foodname == 'tomate cerise'
    assert taxon == '001' # fruit

    # test text2food
    foodname,fid,taxon,score = shelf.text2food(food_name='carotttte', threshold=0.)
    assert foodname == 'carotte'
    assert taxon == '002'

    foodname,fid,taxon,score = shelf.text2food(food_name="250± g de shrim&ps βßdécortiquées (surgelées)", threshold=0.)
    assert foodname == 'shrimp'
    assert taxon.startswith('2') # non vege

    foodname,fid,taxon,score = shelf.text2food(food_name="Lasagne", threshold=0.)
    assert foodname == 'lasagne'

    foodname,fid,taxon,score = shelf.text2food(food_name="Bechamel", threshold=0.)
    assert foodname == 'bechamel'

    foodname,fid,taxon,score = shelf.text2food(food_name="Zuchini", threshold=0.)
    assert foodname == 'zucchini'

    foodname,fid,taxon,score = shelf.text2food(food_name="Apple±eee", threshold=0.)
    assert foodname == 'apple'

    foodname,fid,taxon,score = shelf.text2food(food_name="300g pommes (vertes)", threshold=0.)
    assert foodname == 'pomme'

def test_process_ingredients():
    ''' Test shelf class'''

    # load shelf from region, lang_source and month_id
    from utils import Shelf
    shelf = Shelf(region="France", lang_source="un", month_id=7)

    # get seasonal info
    seasonal_food = shelf.get_seasonal_food(key='001')
    assert 'Tomate' in seasonal_food

    # get link to pictures
    urls = shelf.get_urls(seasonal_food)
    assert 'https://' in urls[0]

    # test Named Entity Recognizer (NER)
    my_recipe_vector, foodnames, qties, unities, taxons, HS, HS_id = shelf.NER(food_list=['tomates','kiwi','sucre'], qty_list=['1','1','1'], unit_list=['kg','default','g'], lang_dest=None)
    assert 'tomate' in foodnames
    assert 'kiwi' not in foodnames

    recipe_vector, foodnames, qties, units, taxons, HS, HS_id = shelf.NER(food_list=["apple"], qty_list=None, unit_list=None, lang_dest=None)
    assert foodnames == ['apple']

    # test process_ingredients
    shelf.process_ingredients(food_list=['poire', 'pomme', 'cerise', 'fraise'], qty_list=['1','1','1'], unit_list=['g','g','g'], lang_dest='fr', infer_nutri=True, revisit=False, serving=2)
    assert 'ingredients' in shelf.tags.keys()
    assert 'HS' in shelf.tags.keys()
    assert 'revisited' in shelf.tags.keys()
    assert 'labels' in shelf.tags.keys()
    assert shelf.tags['labels']['seasonality']['score'] >= 0. and shelf.tags['labels']['seasonality']['score'] <= 100.0
