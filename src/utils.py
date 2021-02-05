
from unidecode import unidecode
import numpy as np
from fuzzywuzzy import fuzz
import pandas as pd
import collections
import json
import requests
import logging
import numpy as np
import os
import glob
import re

logger = logging.getLogger(__name__)

def get_logger(name, output_file):
    log_format = '%(asctime)s  %(name)8s  %(levelname)5s  %(message)s'
    logging.basicConfig(level=logging.INFO,
                        format=log_format,
                        filename=output_file,
                        filemode='w')

    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    console = logging.StreamHandler()
    #console.setLevel(logging.DEBUG)
    console.setLevel(logging.WARNING)

    console.setFormatter(logging.Formatter(log_format))
    logging.getLogger(name).addHandler(console)
    return logging.getLogger(name)

def get_visited(dir_output):

    json_files = sorted(glob.glob(str(dir_output) + "/*.json"))

    data = []

    for output_file in json_files:
        logger.info(output_file)

        try:
            with open(output_file) as f:
                for line in f:
                    json_data = json.loads(line)
                    seller_id = int(json_data['seller_id'])
                    data.append(seller_id)
        except:
            pass

    logger.info(f"Se han descargado info de {len(data)} sellers")

    return data


def df_to_int(df):

    new_df = df.copy()
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']

    columns = new_df.select_dtypes(include=numerics).columns.tolist()
    for col in columns:
        new_df[col] = new_df[col].fillna(-1).astype('int')

    return new_df




def getStartingUrls(file_urls, start, n_cat):

    allowed_domains = ['listado.mercadolibre.com.ar', 'articulo.mercadolibre.com.ar']

    with open(file_urls) as f:
        content = f.readlines()

    content = [x.replace(',','').replace("'","").strip() for x in content]
    start_urls = content[start:start+n_cat]

    for url in start_urls:
        domain = re.findall(r"\w+:?(?=.)", url)[1]
        domain_url = domain + '.mercadolibre.com.ar'
        if domain_url not in allowed_domains:
            allowed_domains.append(domain_url)

    return start_urls, allowed_domains


def get_token(CLIENT_ID, SECRET_KEY, SERVER_GENERATED_AUTHORIZATION_CODE, REDIRECT_URI):
    
    headers = {
        'accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded',
    }

    data = {
      'grant_type': 'authorization_code',
      'client_id': CLIENT_ID,
      'client_secret': SECRET_KEY,
      'code': SERVER_GENERATED_AUTHORIZATION_CODE,
      'redirect_uri': REDIRECT_URI
    }

    try:

        response = requests.post('https://api.mercadolibre.com/oauth/token', headers=headers, data=data).json()

        if not 'error' in response.keys():
            ACCESS_TOKEN = response['access_token']
            REFRESH_TOKEN = response['refresh_token']
        else:
            logger.info(f"{response['message']}")
            raise ValueError(f"{response['message']}")
     

    except requests.exceptions.RequestException as e:  # This is the correct syntax
        logger.info(e)
        print(e)
        raise SystemExit(e)


    return ACCESS_TOKEN, REFRESH_TOKEN

def refresh_token(CLIENT_ID, SECRET_KEY, REFRESH_TOKEN):

    headers = {
        'accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded',
    }

    data = {
      'grant_type': 'refresh_token',
      'client_id': CLIENT_ID,
      'client_secret': SECRET_KEY,
      'refresh_token': REFRESH_TOKEN
    }

    try:

        response = requests.post('https://api.mercadolibre.com/oauth/token', headers=headers, data=data).json()
     

    except requests.exceptions.RequestException as e:  # This is the correct syntax
        logger.info(e)
        print(e)
        raise SystemExit(e)


    return response

