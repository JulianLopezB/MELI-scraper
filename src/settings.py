from pathlib import Path
import os

input_path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / 'inputs'

CREDENTIALS = {
                  'CLIENT_ID': '',
                  'REDIRECT_URI': '',
                  'SECRET_KEY': '',
                  'SERVER_GENERATED_AUTHORIZATION_CODE': '',
                  'REFRESH_TOKEN': ''
        }


SETTINGS = {

            # Conf 1

            'DOWNLOADER_MIDDLEWARES': {
            'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'random_useragent.RandomUserAgentMiddleware': 400
            },

            # Random user_agents
            'USER_AGENT_LIST': str(input_path/"suseragents.txt"),

            # LOGS
            'LOG_ENABLED': False,
            'LOG_PROPAGATE': False,
            'LOG_LEVEL': 'INFO',

            # TIMEOUT
            'CLOSESPIDER_TIMEOUT': 7 * 60 * 60,

            # CONCURRENCY SETTINGS

            'CONCURRENT_REQUESTS': 25, #1000, #25
            'COOKIES_ENABLED': False,
            'CONCURRENT_REQUESTS_PER_DOMAIN': 1, #1000, #50
            'CONCURRENT_REQUESTS_PER_IP': 25, # 1000, #50
            #'RANDOMIZE_DOWNLOAD_DELAY': 1,
            'DOWNLOAD_DELAY': 2,
            'RETRY_HTTP_CODES' : [403], # add here any status codes you receive when getting banned
            'RETRY_TIMES' : 10

        }
