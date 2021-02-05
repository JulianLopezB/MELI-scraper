from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
#from itemloaders.processors import MapCompose
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging, _get_handler
from scrapy.utils.project import get_project_settings
from scrapy.http.request import Request
from src.settings import SETTINGS, CREDENTIALS
from src.utils import *
from bs4 import BeautifulSoup
from datetime import datetime
from time import time
import json
import requests
import random
import re
import scrapy
import argparse
import pathlib
import os

# ARGS
parser = argparse.ArgumentParser()

parser.add_argument('-s', '--start', default=0, type=int,
                    help="Starting point from category list (inputs/starting_urls.txt): int")

parser.add_argument( '-n', '--ncat', default=401, type=int,
                    help="Number of categories to crawl")


args = parser.parse_args()

# PATHS
dir_trabajo = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
dir_output = dir_trabajo / 'outputs'
output_file = dir_output / f"output-{datetime.today().strftime('%Y%m%d')}.json"
dir_input = dir_trabajo / 'inputs'
file_urls = dir_input / 'starting_urls.txt'
logs_path = dir_trabajo / 'logs'

# CREATE PATHS

if not os.path.exists(dir_input):
    raise Exception('Input folder no existe')

for path in [logs_path, dir_output]:

    if not os.path.exists(path):
        os.makedirs(path)
        print(f'Path {path} created')


# CREATE LOGGER
logger = get_logger('SPIDER', logs_path / '{:%Y-%m-%d}.log'.format(datetime.now()))


# PARAMS:
FROM = args.start
NCATS = args.ncat

global CLIENT_ID
global REDIRECT_URI
global SECRET_KEY
global SERVER_GENERATED_AUTHORIZATION_CODE
#global ACCESS_TOKEN
global REFRESH_TOKEN
global FILTER_TAGS
global STARTING_URLS
global ALLOWED_DOMAINS
global SELLERS_VISITED

CLIENT_ID = CREDENTIALS['CLIENT_ID']
REDIRECT_URI = CREDENTIALS['REDIRECT_URI']
SECRET_KEY = CREDENTIALS['SECRET_KEY']
SERVER_GENERATED_AUTHORIZATION_CODE = CREDENTIALS['SERVER_GENERATED_AUTHORIZATION_CODE']
REFRESH_TOKEN = CREDENTIALS['REFRESH_TOKEN']

FILTER_TAGS = ["brand", "large_seller", "eshop", "mshops"]
STARTING_URLS = getStartingUrls(file_urls, FROM, NCATS)[0]
ALLOWED_DOMAINS = getStartingUrls(file_urls, FROM, NCATS)[1]
SELLERS_VISITED = get_visited(dir_output)

# Random shuffle de las start_urls:
random.shuffle(STARTING_URLS)



class MercadoLibreCrawler(CrawlSpider):

    name = 'mercadoLibre'


    allowed_domains = ALLOWED_DOMAINS

    start_time = time()
    response = refresh_token(CLIENT_ID, SECRET_KEY, REFRESH_TOKEN)

    if not 'error' in response.keys():
                        ACCESS_TOKEN = response['access_token']
                        REFRESH_TOKEN = response['refresh_token']
                        logger.info(f'New ACCESS TOKEN: {ACCESS_TOKEN}')
    else:
        logger.info(f"{response['message']}")
        raise ValueError(f"{response['message']}")



    download_delay = 1


    # Reglas
    rules = (
            Rule(
                LinkExtractor(
                    allow=r'/_Desde_\d+'
                ), follow=True),
            Rule(
                LinkExtractor(
                    allow=r'/MLA-'
                ), follow=True, callback='parse_items'),
            )


    def start_requests(self):
        logger.info(f"Crawling {len(STARTING_URLS)} categories")
        string = '\n' + '\n'.join(STARTING_URLS)
        logger.info(f"{string}")
        for start_url in STARTING_URLS:
            yield Request(url=start_url, meta={"start_url": start_url})

      logger.info(f'User agent: {response.request.headers["User-Agent"]}')

    def extract_number(self, texto):
        list_numbers =  [int(s) for s in texto.split() if s.isdigit()]
        return None if len(list_numbers)==0 else list_numbers[0]

    def clean_text(self, texto):
        return texto.replace('\n', ' ').replace('\r', ' ').replace(' ', '')

    def get_item_id(self, response):
        URL = response.request.url
        item_id = 'MLA' + re.findall(r'%s(\d+)' % 'MLA', URL.replace('-',''))[0]
        return item_id

    def get_root_cat(self, category_id):
        r = requests.get(f'https://api.mercadolibre.com/categories/{category_id}').json()
        root_cat = r['path_from_root'][0]['name']
        return root_cat

    def get_item_info(self, item_id):

        seller_id = None
        seller_address = None

        try:
            r = requests.get(f'https://api.mercadolibre.com/items?ids={item_id}').json()[0]
            seller_id = r['body']['seller_id']
            seller_address = r['body']['seller_address']

        except:
            pass

        return seller_id, seller_address


    def get_sold_quantity(self, item):

        if 'sold_quantity' in item.keys() and 'catalog_listing' in item.keys():

            sold_quantity = item['sold_quantity']

        else:
            try:

                link=requests.get(item['permalink'])
                soup=BeautifulSoup(link.text, 'html.parser')
                sold_text = soup.find('span', class_='ui-pdp-subtitle').text
                #logger.info(f'{sold_text}')
                sold_quantity = self.extract_number(sold_text)

                if not sold_quantity:

                    sold_quantity = item['sold_quantity']

                else:
                    pass


            except:

                sold_quantity = 0

        return sold_quantity

    def get_revenue(self, list_items):

        revenue = 0
        ventas = 0
        categorias = []

        if not list_items:
            return ventas, revenue, categorias

        for i in range(len(list_items)):

            item = list_items[i]
            #logger.info(f'Procesando item {i}')

            if 'price' in item.keys():
                price = item['price']
            else:
                price = 0

            if 'category_id' in item.keys():
                categoria = self.get_root_cat(item['category_id'])
            else:
                categoria = None

            sold_quantity = self.get_sold_quantity(item)

            revenue += sold_quantity*price
            ventas += sold_quantity

            if categoria and (categoria not in categorias):
                categorias.append(categoria)

        return ventas, revenue, categorias


    def seller_partial_info(self, seller_id, i):

        headers = {
            'Authorization': f"Bearer {self.ACCESS_TOKEN}"
        }

        params = (
            ('seller_id', str(seller_id)),
            ( 'offset', i)
        )

        r = requests.get('https://api.mercadolibre.com/sites/MLA/search', 
                         headers=headers, 
                         params=params)
        
        return r.json()

    def get_seller_info(self, seller_id):

        if not seller_id:
            return None

        logger.info(f'Buscando resultados del {seller_id}')
        # Init
        seller_info = dict()
        seller_info['time'] = datetime.now()
        seller_info['seller_id'] = seller_id
        seller_info['data'] = None
        seller_results = []
        len_results = 0
        change = True
        i = 0
        count = 0

        while True:

            if time() - self.start_time > 20000:
                    logger.info(f"ACCESS TOKEN {self.ACCESS_TOKEN} about to expire")
                    logger.info(f"REFRESH TOKEN {self.REFRESH_TOKEN} about to expire")

                    response = refresh_token(CLIENT_ID, SECRET_KEY, self.REFRESH_TOKEN)
                    logger.info(response)

                    if not 'error' in response.keys():
                        self.ACCESS_TOKEN = response['access_token']
                        self.REFRESH_TOKEN = response['refresh_token']
                        logger.info(f'New ACCESS TOKEN: {self.ACCESS_TOKEN}')
                    else:
                        logger.info(f"{response['message']}")
                        raise ValueError(f"{response['message']}")
                    self.start_time = time()


            if count == 5:
                break

            try:
                
                r = self.seller_partial_info(seller_id, i)

                if i==0:

                    
                    if not 'seller' in r.keys():
                        break

                    if r['seller']['real_estate_agency'] or r['seller']['car_dealer']:
                        logger.info(f'{seller_id} is real_estate_agency or car_dealer')
                        break

                    r['seller'].pop('real_estate_agency', None)
                    r['seller'].pop('car_dealer', None)

                    seller_info['data'] = r['seller']

                    if not any([tag in seller_info['data']['tags'] for tag in FILTER_TAGS]):
                        info.logger('f{seller_id} NOT a company')
                        break
                    
                seller_results += r['results']
                old_len_results = len_results
                len_results = len(seller_results)

                if len_results == old_len_results:
                    break

                i += 50
                count = 0

            except:
                count += 1


        if not seller_info['data']:
            logger.info(f'No se ha registrado info del seller {seller_id}')
            return None

        logger.info(f'Se encontraron {len_results} resultados del {seller_id}')
        seller_info['data']['cantidad_articulos'] = len_results
        ventas, revenue, categorias = self.get_revenue(seller_results)
        seller_info['data']['cantidad_ventas'] = ventas
        seller_info['data']['revenue'] = revenue
        seller_info['data']['categorias'] = categorias

        if seller_results:
            seller_info['seller_address_2'] = seller_results[0]['seller_address']

        return seller_info


    def parse_items(self, response):

        item_id = self.get_item_id(response)
        item_info = self.get_item_info(item_id)
        seller_id = item_info[0]
        seller_address = item_info[1]

        if seller_id not in SELLERS_VISITED:
            logger.info(f'NUEVO. (seller_id: {seller_id})')
            seller_info = self.get_seller_info(seller_id)
            if seller_info:
                seller_info['seller_address'] = seller_address
                SELLERS_VISITED.append(seller_id)
                logger.info('Guardado en SELLERS_VISITED.txt')
                logger.info('Registrado en outputs.json')
                yield seller_info
            else:
                logger.info('Sin info')
                pass
        else:
            logger.info(f'Ya visitado. (seller_id: {seller_id})')




def crawl():

    logger.info(f'Se iniciara la descarga en {output_file}')
    SETTINGS['FEEDS'] = {'file:///' + str(output_file): {'format': 'jsonlines'}}
    logger.info(SETTINGS['FEEDS'])
    

    s = get_project_settings()
    for k, v in SETTINGS.items():
        s.update({
            k: v
        })

    proc = CrawlerProcess(s)

    proc.crawl(MercadoLibreCrawler, 'dummyinput')
    proc.start()



if __name__ == "__main__":

    crawl()
