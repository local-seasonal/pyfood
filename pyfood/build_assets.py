import os
import pandas as pd
import numpy as np
import json
import pickle
import matplotlib.pyplot as plt
import re
import unidecode
from math import radians, cos, sin, asin, sqrt
from scipy.sparse import csr_matrix, save_npz, load_npz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict


def sort_vocab(assets_paths:str='./assets', verbose:int=1):
    """ 
    Sort csv file by taxon and french names

    Args:
        assets_paths (str): Path to assets
        verbose (int): Verbose level
    """

    ### Load vocab from csv, sort vocab and save result
    df = pd.read_csv(os.path.join(assets_paths,'vocab/vocab.csv')) # fr, en, es, it, pt, de, zh + taxons
    df['taxon'] = df['taxon'].astype(int)
    df = df.sort_values(['taxon', 'fr'])
    df.to_csv(os.path.join(assets_paths,'vocab/vocab.csv'), index=False)


def build_mapping(assets_paths:str='./assets', verbose:int=1) -> Dict:
    """ 
    Build universal mapping from csv file: ingredients <-> food id. Save and store food attributes by id (taxon, names, default_weight, density, kCal, vitamins, allergen, etc.)

    Args:
        assets_paths (str): Path to assets
        verbose (int): Verbose level

    Returns:
        dict: Mapping between food name and id in dict[lang]['f2id'] and dict[lang]['id2f'].
    """

    ### Load vocab from csv
    df = pd.read_csv(os.path.join(assets_paths,'vocab/vocab.csv')) # fr, en, es, it, pt, de, zh + taxons
    languages = list(df.columns)[:-1] # fr, en, es, it, pt, de, zh
    assert len(languages) == 7

    reference_names = {}
    for lang_ in languages:
        reference_names[lang_] = [] 
    reference_taxons = [] # Taxon (001, 002 ... 101 ...)

    for row in df.values:
        taxon_id = ''.join(['0']*(3-len(str(row[-1])))) + str(row[-1])
        reference_taxons.append(taxon_id)
        assert int(float(taxon_id)) >= 0
        for lang_, names in zip(languages, row[:-1]):
            reference_names[lang_].append(names.split('&')[0])

    for lang_ in languages:
        reference_names[lang_] = np.array(reference_names[lang_])

    ### Create universal mapping fruit/veg - id
    n = len(reference_names[languages[0]]) # number of unique ingredients... (for Basket of Food representation)
    ids_ = np.arange(n, dtype=float) # Food ID
    mapping = {}
    for lang_ in languages:
        mapping[lang_] = {
                            'f2id':dict(zip(reference_names[lang_], ids_)), # fruit/veg to unique id
                            'id2f':dict(zip(ids_, reference_names[lang_])) # id to fruit/veg
                        }

    ### Add synonyms & az encoding (no special characters)
    for row in df.values:
        #taxon_id = ''.join(['0']*(3-len(str(row[-1])))) + str(row[-1])
        for lang_, names in zip(languages, row[:-1]):
            names_list = names.split('&')
            names_list_az = [re.sub('[^a-zA-Z]+', ' ',  unidecode.unidecode(food_name)).strip() for food_name in names_list] # convert utf-8 unicode with accents to unaccented_string, replace apostrophees, non alpha characters by spaces and strip string
            names_list_az = [food_name for food_name in names_list_az if food_name not in names_list]
            names_list = names_list + names_list_az
            if len(names_list)>1: # more than one name
                ref = names_list[0]
                for synonyms in names_list[1:]:
                    #print(lang_, ref, synonyms)
                    mapping[lang_]['id2f'][float(len(mapping[lang_]['id2f']))] = synonyms # add synonyms id2f (high id)
                    mapping[lang_]['f2id'][synonyms] = mapping[lang_]['f2id'][ref] # add mapping f2id (low id)

    ### add universal language, initiated with fr
    mapping["un"] = {'f2id': {}, "id2f":{}}
    for lang_ in languages:
    	for fid_, fname_ in mapping[lang_]["id2f"].items(): # high id
    		if fname_ not in mapping["un"]["f2id"]:
	    		idx = float(len(mapping["un"]["id2f"]))
    			mapping["un"]["id2f"][idx] = fname_
    			mapping["un"]["f2id"][fname_] = mapping[lang_]['f2id'][fname_] # mapping f2id (low id) 
    print("universal language: ", len(mapping["un"]["id2f"]), len(mapping["un"]["f2id"]))


    ### Save mapping
    with open(os.path.join(assets_paths,'vocab/mapping.json'), 'w') as fp:
        json.dump(mapping, fp, indent=4)

    ### Read and write feats.json 
    with open(os.path.join(assets_paths,'vocab/feats.json'), 'r') as fp:  ##### assert path exists (else init!)
        feats = json.load(fp)     
    #with open(os.path.join(assets_paths,'vocab/feats_old.json'), 'w') as fp:
    #    json.dump(feats, fp, indent=4)

    ### Transfer feats to new_feats
    new_feats = {}
    for fid, taxon in zip(ids_, reference_taxons):
        new_feats[fid] = {'taxon':taxon,
                          'default_weight':10, 'density':1.0, 'allergen':'None', 'url':'None',
                           'CIQUAL_ref':'None', 'kCal':0., 'macro':'None', 'minerals':'None', 'vitamins':'None'} # NB: default_weight in g, default_density in g/ml (=kg/L) 
        new_feats[fid]["un"] = reference_names["fr"][int(fid)] # fr = un language (ref)
        for lang_ in languages:
            new_feats[fid][lang_] = reference_names[lang_][int(fid)]

    for old_fid, v in feats.items():
        fr_name = v['fr']
        #fr_name_az = re.sub('[^a-zA-Z]+', ' ',  unidecode.unidecode(v['fr'])).strip()
        if fr_name in mapping['fr']['f2id']: # old ingredient in new vocab
            new_fid = mapping['fr']['f2id'][fr_name]
            new_feats[new_fid]['default_weight'] = v['default_weight']
            new_feats[new_fid]['density'] = v['density']
            new_feats[new_fid]['allergen'] = v['allergen']
            new_feats[new_fid]['url'] = v['url']
            new_feats[new_fid]['CIQUAL_ref'] = v['CIQUAL_ref']
            new_feats[new_fid]['kCal'] = v['kCal']
            new_feats[new_fid]['macro'] = v['macro']
            new_feats[new_fid]['minerals'] = v['minerals']
            new_feats[new_fid]['vitamins'] = v['vitamins']
            for nutri in ['macro','minerals','vitamins']:
                if len(new_feats[new_fid][nutri])==0:
                    new_feats[new_fid][nutri] = 'None'

        #elif fr_name_az in mapping['fr']['f2id']: # old ingredient in new vocab
        #    new_fid = mapping['fr']['f2id'][fr_name]
        #    new_feats[new_fid]['default_weight'] = v['default_weight']
        #    new_feats[new_fid]['density'] = v['density']
        #    new_feats[new_fid]['allergen'] = v['allergen']
        #    new_feats[new_fid]['url'] = v['url']
        #    new_feats[new_fid]['CIQUAL_ref'] = v['CIQUAL_ref']
        #    new_feats[new_fid]['kCal'] = v['kCal']
        #    new_feats[new_fid]['macro'] = v['macro']
        #    new_feats[new_fid]['minerals'] = v['minerals']
        #    new_feats[new_fid]['vitamins'] = v['vitamins']
        #    for nutri in ['macro','minerals','vitamins']:
        #        if len(new_feats[new_fid][nutri])==0:
        #            new_feats[new_fid][nutri] = 'None'

    with open(os.path.join(assets_paths,'vocab/feats.json'), 'w') as fp:
        json.dump(new_feats, fp, indent=4)

    if verbose>0:
        print('\n -- Ran script build_mapping --')
        print(df.head(5))
        print('Sanity check 1 for {} unique food: {}'.format(n, len(reference_names['fr'])==len(reference_names['es']) and len(reference_names['en'])==len(reference_names['it'])))
        print('Saved', os.path.join(assets_paths,'vocab/mapping.json'), '\n')
        print('Sanity check 2: {}'.format(len(new_feats)==len(reference_names['fr'])))
        print('Saved', os.path.join(assets_paths,'vocab/feats.json'), '\n')

        ### Check duplicate names
        for lang_ in ["un"] + languages:
            duplicates = set()
            for i,n1 in mapping[lang_]['id2f'].items():
                for j,n2 in mapping[lang_]['id2f'].items():
                    if i<j and n1==n2:
                        duplicates.add(n1)
            if len(duplicates)>0:
                print('WARNING {}: {}'.format(lang_, ', '.join(duplicates)))

    return mapping


def build_charagrams(mapping:Dict, assets_paths:str='./assets', verbose:int=1):
    """ 
    Build a NLP vectorizer for fast IR. Store bag of ngrams for ingredient retrieval.

    Args:
        mapping (dict): Mapping between food name and id in dict[lang]['f2id'] and dict[lang]['id2f'].
        assets_paths (str): Path to assets
        verbose (int): Verbose level
    """ 

    import warnings
    warnings.simplefilter("ignore")

    tfidf = TfidfVectorizer(analyzer='char', ngram_range=(3, 4)) # ngram vectorizer
    for lang in mapping.keys():
        corpus = np.array([v for v in mapping[lang]['id2f'].values()])
        ngrams = tfidf.fit_transform(corpus) # low and high id2f
        pickle.dump(tfidf, open(os.path.join(assets_paths,"vocab/{}/tfidf_{}.pickle".format(lang, lang)), "wb"))
        pickle.dump(ngrams, open(os.path.join(assets_paths,"vocab/{}/ngrams_{}.pickle".format(lang, lang)), "wb"))

        if verbose>0:
            print('\n -- Ran script build_charagrams --')
            print('Sanity check {}: {}'.format(lang, ngrams.shape[0]>=len(mapping))) # synonymes
            print(lang,':',ngrams.shape)
            print('Saved', os.path.join(assets_paths,"vocab/{}/tfidf_{}.pickle".format(lang, lang)))
            print('Saved', os.path.join(assets_paths,"vocab/{}/ngrams_{}.pickle".format(lang, lang)))


def build_nutriscores(assets_paths:str='./assets', plot_matrix:bool=True, verbose:int=1):
    """  Build a sparse nutriscore matrix. NB: Default weight in g and density in g/ml (=kg/L).

    Args:
        assets_paths (str): Path to assets
        plot_matrix (bool) Plot nutriscores
        verbose (int): Verbose level
    """ 

    with open(os.path.join(assets_paths, 'nutri/nutrimap.json'), 'r') as fp:
        nutrimap = json.load(fp)
        nutrikeys = [kk for d in nutrimap.values() for kk in d.keys()]

    with open(os.path.join(assets_paths, 'nutri/vnr.json'), 'r') as fp:
        vnr = json.load(fp)
        #vnr = [vv for d in vnr.values() for vv in d.values()]

    with open(os.path.join(assets_paths, 'vocab/feats.json'), 'r') as fp:
        feats = json.load(fp)

    dense_scores = np.zeros((len(nutrikeys), len(feats))) #  nutriscores <-> ingredients (FR, ESP, EN) 
    for fid, v in feats.items():
        j = int(float(fid))

        # Energy
        i = int(nutrimap['Energy']['kCal'])
        dense_scores[i][j] = v['kCal']/float(vnr['Energy']['kCal']) # kCal pour 100 g

        # Macro
        if v['macro']!='None':
            for line in v['macro'].split(','):
                compo, percent = line.split(':')[0].strip(), float(line.split(':')[1])
                i = int(nutrimap['Macro'][compo])
                dense_scores[i][j] = percent/float(vnr['Macro'][compo]) # g pour 100 g

        # Minerals
        if v['minerals']!='None':
            for line in v['minerals'].split(','):
                compo, percent = line.split(':')[0].strip(), float(line.split(':')[1])
                i = int(nutrimap['Minerals'][compo])
                dense_scores[i][j] = percent/float(vnr['Minerals'][compo]) # mg pour 100 g except (I & Se µg/g)

        # Vitamines
        if v['vitamins']!='None':
            for line in v['vitamins'].split(','):
                compo, percent = line.split(':')[0].strip(), float(line.split(':')[1])
                i = int(nutrimap['Vitamins'][compo])
                dense_scores[i][j] = percent/float(vnr['Vitamins'][compo]) # mg pour 100 g except (Beta-carotene & B9 µg/g)

    top_k = 4
    s = 0.00001 # % VNR
    ranked_nutri_idx = np.argsort(dense_scores,axis=0)[::-1]
    for fid in range(ranked_nutri_idx.shape[1]):
        #feats[str(float(fid))]['top_Macro'] = [nutrikeys[nutri_label_idx] for nutri_label_idx in ranked_nutri_idx[:,fid] if nutrikeys[nutri_label_idx] in nutrimap['Macro'].keys() and dense_scores[nutri_label_idx][fid]>s][:top_k]
        feats[str(float(fid))]['top_Minerals'] = [nutrikeys[nutri_label_idx] for nutri_label_idx in ranked_nutri_idx[:,fid] if nutrikeys[nutri_label_idx] in nutrimap['Minerals'].keys() and dense_scores[nutri_label_idx][fid]>s][:top_k]
        feats[str(float(fid))]['top_Vitamins'] = [nutrikeys[nutri_label_idx] for nutri_label_idx in ranked_nutri_idx[:,fid] if nutrikeys[nutri_label_idx] in nutrimap['Vitamins'].keys() and dense_scores[nutri_label_idx][fid]>s][:top_k]

    with open(os.path.join(assets_paths,'vocab/feats.json'), 'w') as fp:
        json.dump(feats, fp, indent=4)

    sparse_nutriscores = csr_matrix(dense_scores)
    save_npz(os.path.join(assets_paths, 'nutri/sparse_nutriscores.npz'), sparse_nutriscores)

    if verbose>0:
        print('\n -- Ran script build_nutriscores --')
        print('Saved {}'.format(os.path.join(assets_paths, 'nutri/feats.json')))
        print('Saved {}'.format(os.path.join(assets_paths, 'nutri/sparse_nutriscores.npz')))

    if plot_matrix:
        dense = dense_scores
        dense = dense-np.expand_dims(dense.min(axis=1),1)
        dense /= np.expand_dims(dense.max(axis=1), axis=1) # Normalize attributes (between 0 and 1)
        plt.imshow(dense, cmap='tab20c')
        plt.yticks(np.arange(dense.shape[0]), nutrikeys, rotation=0)
        plt.xlabel('Food')
        plt.title('Nutri scores')
        plt.colorbar()
        plt.show()
        

def build_temporada(region:str='Granada', lang_source:str='es', plot_matrix:bool=False, assets_paths:str='./assets', verbose:int=1):
    """ Build a sparse seasonality matrix from two text files (local-seasonal + permanent)

    Args:
        assets_paths (str): Path to assets
        region (str): Region of interest
        lang_source (str): .txt file language
        plot_matrix (bool): Plot seasonal matrix
        verbose (int): Verbose level
    """ 

    with open(os.path.join(assets_paths,'vocab/feats.json'), 'r') as fp:
        feats = json.load(fp)

    with open(os.path.join(assets_paths,'vocab/mapping.json'), 'r') as fp:
        mapping = json.load(fp)[lang_source] # food univeral mapping (f2id, id2f)

    tfidf = pickle.load(open(os.path.join(assets_paths,'vocab/{}/tfidf_{}.pickle'.format(lang_source, lang_source)), "rb")) # ngram vectorizer for food names
    ngrams = pickle.load(open(os.path.join(assets_paths,'vocab/{}/ngrams_{}.pickle'.format(lang_source, lang_source)), "rb"))

    NU = set() ### Non retrieved from .txt file.
    RN = set() ### Renamed 
    duplicates = {0:set(), 1:set(), 2:set(), 3:set(), 4:set(), 5:set(), 6:set(), 7:set(), 8:set(), 9:set(), 10:set(), 11:set(), 12:set()}

    def text2food(food:str='apple', threshold:float=0.55):
        food = food.lower().strip()
        if food in f2id:
            fid = int(f2id[food])
            return food, fid
        if len(food)==0:
            return food, None
        affinity = cosine_similarity(tfidf.transform([food]), ngrams, dense_output=True) # (1, n_ingredients)
        nearest_neighbor = np.argmax(affinity, axis=1)
        for id_ in nearest_neighbor:
            if affinity[:,id_]>threshold:
                food_ = id2f[str(float(id_))]
                fid = f2id[food_]
                RN.add('{} >> {}'.format(food, food_))
                return food_, int(fid)
        NU.add('_{}_'.format(food))
        return food, None

    ### Load universal mapping (food2id)
    f2id = mapping['f2id'] # fruit/veg to low id
    id2f = mapping['id2f']
    n_seasonal = len([fid for fid,v in feats.items() if int(v['taxon'][0])==0]) # number of seasonal ingredients (for BOW representation)
    n_ingredients = len(feats) # total number of ingredients

    ### Load/save knowledge (seasonality in given region)
    sparse_seasonality = np.zeros((12, n_ingredients))

    # Local-seasonal fruits&vegs
    with open(os.path.join(assets_paths,'seasons/input/{}/{}_localseasonal.txt'.format(region, region)), 'r', encoding='utf-8-sig') as fp: 
        for month_id, foodlist in enumerate(fp.readlines()):
            foodlist = foodlist.replace('\n','').strip()
            for food in foodlist.split(','):
                food, fid = text2food(food=food)
                if fid is not None:
                    if sparse_seasonality[month_id][fid]>0.:
                        duplicates[month_id].add(food)
                    sparse_seasonality[month_id][fid] = 1.                        

            # Aseasonal food: +50 (all year)
            for fid in range(n_seasonal, n_ingredients):
                if not feats[str(float(fid))]['taxon'].startswith('21'): # discard meat, fish, eggs, seafood
                    if sparse_seasonality[month_id][fid]>0.:
                        duplicates[month_id].add(id2f[str(float(fid))])
                    sparse_seasonality[month_id][fid] = 0.5

    # Permanent legumineuse & conserved food (all year low carbon)
    with open(os.path.join(assets_paths,'seasons/input/{}/{}_permanent.txt'.format(region, region)), 'r', encoding='utf-8-sig') as fp: 
        #foodlist = fp.readlines()[0].replace('\n','').strip()
        foodlist = fp.readlines()
        for food in foodlist:
            food, fid = text2food(food=food.replace('\n',''))
            if fid is not None:
                for month_id in range(12):
                    if sparse_seasonality[month_id][fid]>0.:
                        duplicates[month_id].add(food)
                    sparse_seasonality[month_id][fid] = 1.

    ### Save sparse matrix
    sparse_seasonality = csr_matrix(sparse_seasonality) # csr_matrix((data, (row, col)), shape=(12, n_ingredients), dtype=np.float) # ingredients (fr, es, en) <-> seasons 
    save_npz(os.path.join(assets_paths,'seasons/sparse_seasons_{}.npz'.format(region)), sparse_seasonality)
    
    fail_months, fail_food = (sparse_seasonality>1.).nonzero()
    if verbose>0:
        print('\n -- Ran script build_temporada in {}--'.format(region))
        if len(RN)>0:
            print('Renamed: ', RN)
        if len(NU)>0:
            print('Non understood: ', NU)
        for k,v in duplicates.items():
            if len(duplicates[k])>0:
                print('duplicates {}: '.format(k+1), duplicates[k])
        if len(fail_months)>0:
            print('Failed:', [feats[str(float(wid))]['fr'] for wid in set(fail_food)], fail_months)
        print('Saved {}'.format(os.path.join(assets_paths,'seasons/sparse_seasons_{}.npz'.format(region))),'\n')

    if plot_matrix:
        dense = sparse_seasonality.toarray() # Col=Food. 224 [1], 279 [2], 3 [316], 4 [365] 5 [-1]
        plt.imshow(dense, cmap='YlGn')
        plt.xlabel('Food')
        plt.title('Seasons scores @{}'.format(region))
        plt.colorbar()
        plt.show()


### Nutri Info (cf. CIQUAL Table) ###
#anses_macro = ['Protéines (g/100g)', 'Glucides (g/100g)', 'AG saturés (g/100g)', 'Acides organiques (g/100g)', 'Sucres (g/100g)', 'Fibres alimentaires (g/100g)', 'Lipides (g/100g)']
#anses_vitamins = ['Beta-Carotène (µg/100g)', 'Vitamine E (mg/100g)', 'Vitamine C (mg/100g)', 'Vitamine B1 ou Thiamine (mg/100g)', 'Vitamine B2 ou Riboflavine (mg/100g)', 'Vitamine B3 ou PP ou Niacine (mg/100g)', 'Vitamine B5 ou Acide pantothénique (mg/100g)', 'Vitamine B6 (mg/100g)', 'Vitamine B9 ou Folates totaux (µg/100g)']
#anses_minerals = ['Calcium (mg/100g)', 'Cuivre (mg/100g)', 'Fer (mg/100g)', 'Iode (µg/100g)', 'Magnésium (mg/100g)', 'Manganèse (mg/100g)', 'Phosphore (mg/100g)', 'Potassium (mg/100g)', 'Sélénium (µg/100g)', 'Sodium (mg/100g)', 'Zinc (mg/100g)']
#anses_energy = ['Règlement UE N° 1169/2011 (kcal/100g)']
#anses_others: Gluten / carbohydrates / cholesterol / fibre / fats (lipides) / unsaturated fats

#app_macro = ['Prot', 'Glucides', 'Acides gras satur', 'Acides organiques', 'Sucre', 'Fibres', 'Lipides'] # MACRO g/100g
#app_vitamins = ['Beta-carotene', 'E', 'C', 'B1', 'B2', 'B3', 'B5', 'B6', 'B9'] # Vitamin mg/100g except [Beta-carotene and B9 µg/100g]
#app_minerals = ['Ca', 'Cu', 'Fe', 'I', 'Mg', 'Mn', 'P', 'K', 'Se', 'Na', 'Zn'] # Mineral mg/100g except [I and Se µg/100g]
#app_energy = ['kCal'] # kCal/100g
##### Add power of minerals, vitamins... (hairs, heart, antioxydant...): Les cuisiniers, les medecins de demain.


def build(assets_paths:str='./assets', verbose:int=1):
    """ Build all assets to power pyfood.

    Args:
        assets (str): Path to assets
        verbose (int): Verbose level
    """

    # sort_vocab(assets_paths=assets_paths, verbose=verbose)
    
    mapping = build_mapping(assets_paths=assets_paths, verbose=verbose)
    build_charagrams(mapping, assets_paths=assets_paths, verbose=verbose)
    build_nutriscores(assets_paths=assets_paths, plot_matrix=False, verbose=verbose)

    # Spatio-temporal knowledge (seasons)
    for region in ['Senegal','Canada','France']:
        build_temporada(region=region, lang_source='fr', plot_matrix=False, assets_paths=assets_paths, verbose=verbose)
    for region in ['United Kingdom','Israel','Japan']:
        build_temporada(region=region, lang_source='en', plot_matrix=False, assets_paths=assets_paths, verbose=verbose)
    for region in ['Italy']:
        build_temporada(region=region, lang_source='it', plot_matrix=False, assets_paths=assets_paths, verbose=verbose)
    for region in ['Spain']:
        build_temporada(region=region, lang_source='es', plot_matrix=False, assets_paths=assets_paths, verbose=verbose)
    for region in ['Portugal']:
        build_temporada(region=region, lang_source='pt', plot_matrix=False, assets_paths=assets_paths, verbose=verbose)
    for region in ['Germany']:
        build_temporada(region=region, lang_source='de', plot_matrix=False, assets_paths=assets_paths, verbose=verbose)

    # Europe Macro Region
    EU = ['France', 'United Kingdom', 'Italy', 'Spain', 'Portugal', 'Germany']
    sparse_seasonality = csr_matrix(np.max([load_npz(os.path.join(assets_paths,'seasons/sparse_seasons_{}.npz'.format(region))).toarray() for region in EU], 0))
    save_npz(os.path.join(assets_paths,'seasons/sparse_seasons_EU.npz'), sparse_seasonality)


if __name__=='__main__':
    build()