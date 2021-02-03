import json
from pathlib import Path
import json
import os
import io
import time
import argparse
from datetime import datetime
import sys
sys.path.append('../')
from src.process_data import *
from src.utils import *


 # PATHS
dir_trabajo = Path(os.path.dirname(os.path.abspath(__file__)))

output_path = dir_trabajo / 'outputs'
input_path = dir_trabajo / 'inputs'
logs_path = dir_trabajo / 'logs'

empresas_path = input_path / 'registro-nacional-sociedades-202009.csv'


match_path = output_path / f"match-{datetime.today().strftime('%Y%m%d')}.json"
log_path = f"../MELI-scraper/outputs/output-{datetime.today().strftime('%Y%m%d')}.json"   #Tiene que apuntar a MELI-scraper/outputs/output.json

logger = get_logger('PROCESS', logs_path / 'matching_{:%Y-%m-%d}.log'.format(datetime.now()))


VISITED_MATCHED = get_visited(output_path)
logger.info(f'Se ha matcheado {len(VISITED_MATCHED)} vendedores')

# def tail(stream_file):
#     """ Read a file like the Unix command `tail`.
#     Code from https://stackoverflow.com/questions/44895527/reading-infinite-stream-tail """
#     logger.info(f'Streamming {stream_file}')
#     #stream_file.seek(0, os.SEEK_END)  # Go to the end of file
#     stream_file.seek(0, os.SEEK_SET)  # Go to the beginning of file
#     while not stream_file.closed:
#         line = stream_file.readline()
#         yield line

def tail(stream_file):
    logger.info(f'Streamming {stream_file}')
    """ Read a file like the Unix command `tail`. Code from https://stackoverflow.com/questions/44895527/reading-infinite-stream-tail """
    stream_file.seek(0, os.SEEK_END)  # Go to the end of file

    while True:
        if stream_file.closed:
            logger.info(f'File {stream_file} closed')
            raise StopIteration
            #sys.exit(exitCodeYouFindAppropriate)

        line = stream_file.readline()

        yield line

def log_to_db(log_path, db):
    """ Read log (JSON format) and insert data in db """
    if os.path.isfile(match_path) and os.access(match_path, os.R_OK):
        # checks if file exists

        old_match_data = []
        with open(match_path, "r") as match_file:
            for line in match_file:
                try:
                    line_info = json.loads(line)
                    old_match_data.append(line_info)
                except:
                    pass

        with open(match_path, "w") as match_file:
            for line in old_match_data:
                json.dump(line, match_file)
                match_file.write('\n')

        VISITED_FILE = [json.loads(line)['seller_id'] for line in open(match_path)]

        logger.info(f"Output file exists and is readable. Matched so far: {len(VISITED_FILE)}")
    else:
        logger.info("Either output file is missing or is not readable, creating file...")

        with io.open(match_path, 'w') as db_file:

            db_file.write(json.dumps(
            {"seller_id": 0, "match": {"data_empresas": None, "party_id": None}, 'matched': False}
            ))
            db_file.write('\n')

            #VISITED_MATCHED = []

    with open(match_path, "r+") as match_file: # r+ o a ?

        match_file.seek(0, os.SEEK_END)

        with open(log_path, "r") as log_file:

            for line in tail(log_file):

                try:

                    log_data = json.loads(line)

                except ValueError:
                    # Bad json format, maybe corrupted...
                    continue  # Read next line

                if log_data['seller_id']:

                    if log_data['seller_id'] not in VISITED_MATCHED:
                        match_data = dict()
                        match_data['seller_id'] = log_data['seller_id']
                        match = match_sellers(log_data, empresas)
                        match_data['match'] = convert_numpy_objects(match)
                        MATCHED = any([match_data['match'][k] for k in ['data_empresas', 'party_id']])
                        match_data['matched'] = MATCHED
                        logger.info(f"Dumping match for {match_data['seller_id']}... Matched: {MATCHED}")
                        json.dump(match_data, match_file)
                        match_file.write('\n')
                    else:
                        logger.info(f"{log_data['seller_id']} already matched")


if __name__ == "__main__":

    # Load and transform empresas data
    logger.info(f'Pre-procesando {empresas_path}')
    empresas = pd.read_csv(empresas_path)
    empresas['name']  = empresas['razon_social'].apply(create_name)
    empresas = df_to_int(empresas)
    empresas.set_index('name', inplace=True)

    for col in ['dom_fiscal_provincia', 'dom_fiscal_localidad']:
        empresas[col] = empresas[col].apply(normalize_address)

    logger.info(f'{empresas_path} procesado con exito')


    log_to_db(log_path, db=None)