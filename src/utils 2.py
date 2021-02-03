
from unidecode import unidecode
import numpy as np
from fuzzywuzzy import fuzz
import pandas as pd
import collections
import logging
import json
import glob
import numpy as np
import os
import re

logger = logging.getLogger(__name__)


def flatten(d, parent_key='', sep='_'):
    
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            if type(v) == list:
                if len(v) == 1:
                    items.append((new_key, v[0]))
                else:
                    items.append((new_key, v))
            else:
                items.append((new_key, v))
    return dict(items)
    

def normalize_text(text):

    text = unidecode(text)
    text = text.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./?\|`~-=_+"})
    text = text.translate({ord(c): " " for c in '"'})
    return text

def normalize_address(address):

    if not pd.isna(address):
        address = normalize_text(address).upper().replace('  ', ' ')
        address = 'CAPITAL FEDERAL' if address == 'CIUDAD AUTONOMA BUENOS AIRES' else address
        return address
    return None

def create_name(razon_social):

    if razon_social:
        name = razon_social.upper()
        name = normalize_text(name)
        name = name.replace(' SA', '').replace(' S A', '')
        name = name.replace(' SRL', '').replace(' S R L', '')
        name = ''.join(name.split())
        return name
    return None


def find_nearest_name(name, name_list, THRESHOLD = 90):

    match = {'name': None, 'score': 0}
    for i in range(len(name_list)):
        d = fuzz.ratio(name, name_list[i])
        if d > match['score']:
            match['score'] = int(d)
            match['name'] = name_list[i]
            if d >= THRESHOLD:
                return match
    return match


def convert_numpy_objects(dict_to_convert : dict) -> dict:
    new = {}
    for k, v in dict_to_convert.items():
        if isinstance(v, dict):
            new[k] = convert_numpy_objects(v)
        else:
            if isinstance(v, float):
                if np.isnan(v) or np.isinf(v):
                    new[k] = None
                else:
                    new[k] = int(v)
            elif isinstance(v, np.int32) or isinstance(v, np.int64):
                new[k] = int(v)
            else:
                new[k] = v
    return new

def sanitize(x):
    if pd.isna(x):
        return None
    else:
        return int(x)

def match_sellers(row, empresas, THRESHOLD = 90):

    nickname = create_name(row['data']['nickname'])
    state_name = normalize_address(row['seller_address']['state']['name'])
    location_name = ''
    neighborhood_name = ''
    if 'search_location' in row['seller_address']:

        if 'city' in row['seller_address']['search_location'].keys():
            location_name = normalize_address(row['seller_address']['search_location']['city']['name'])

        if 'neighborhood' in row['seller_address']['search_location'].keys():
            neighborhood_name = normalize_address(row['seller_address']['search_location']['neighborhood']['name'])

    retrieve_empresas = None
    party_id = None

    if nickname:

        query = '' + \
                f"dom_fiscal_provincia == '{state_name}'" + \
                " and " + f"(dom_fiscal_localidad == '{location_name}'" + \
                " or " + f"dom_fiscal_localidad == '{neighborhood_name}')"

        df = empresas.query(query, engine='python')
        match = find_nearest_name(nickname, df.index.tolist())

        cuit, razon = None, None

        if match['score'] >= THRESHOLD:


            retrieve_empresas = empresas.loc[match['name']]

            if isinstance(retrieve_empresas, pd.Series):

                retrieve_empresas = [convert_numpy_objects(retrieve_empresas.to_dict())]


            elif isinstance(retrieve_empresas, pd.DataFrame):

                retrieve_empresas = [convert_numpy_objects(x) for x in retrieve_empresas.to_dict('records')]

            cuit = [str(int(x['cuit'])) for x in retrieve_empresas]
            razon = [x['razon_social'] for x in retrieve_empresas]
            

        query = '' + \
                (f"(Nro_Doc_cu == @cuit) or " if cuit else '') + \
                f"((provincia == '{state_name}')" + \
                " and " + f"(localidad == '{location_name}'" + \
                " or " + f"localidad == '{neighborhood_name}'))"

    return {'data_empresas': retrieve_empresas}
    

