from pathlib import Path
import os

input_path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / 'inputs'

CREDENTIALS = {
                  'CLIENT_ID': '7009568980355151',
                  'REDIRECT_URI': 'https://mercadolibre.com.ar',
                  'SECRET_KEY': 'z6lCbQU6E6GfbS8EQwOLRXPeTuRkGhIK',
                  'SERVER_GENERATED_AUTHORIZATION_CODE': 'TG-601838957eb5ec000603e3b0-49662383',
                  'REFRESH_TOKEN': 'TG-601838d2513b3600060bd790-49662383'
        }

SETTINGS = {

            # Conf 1

            'DOWNLOADER_MIDDLEWARES': {
            'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'random_useragent.RandomUserAgentMiddleware': 400
            },

            # Random user_agents
            'USER_AGENT_LIST': str(input_path/"suseragents.txt"),

            # 'DOWNLOADER_MIDDLEWARES': {
            #     'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            #     'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            #     'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
            #     'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
            # },

            # 'FAKEUSERAGENT_PROVIDERS': [
            #     'scrapy_fake_useragent.providers.FakeUserAgentProvider',  # this is the first provider we'll try
            #     'scrapy_fake_useragent.providers.FakerProvider',  # if FakeUserAgentProvider fails, we'll use faker to generate a user-agent string for us
            #     'scrapy_fake_useragent.providers.FixedUserAgentProvider',  # fall back to USER_AGENT value
            # ],

            # 'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',

            # LOGS

            'LOG_ENABLED': False,
            'LOG_PROPAGATE': False,
            'LOG_LEVEL': 'INFO',

            # TIMEOUT
            'CLOSESPIDER_TIMEOUT': 7 * 60 * 60,


            # # Concurrency Settings

            # 'DOWNLOAD_DELAY': 0.25, #0.25,
            # 'AUTOTHROTTLE_DEBUG': True,
            # 'AUTOTHROTTLE_ENABLED': True, #True,
            # 'AUTOTHROTTLE_START_DELAY': 2,
            # 'AUTOTHROTTLE_TARGET_CONCURRENCY': 500, #6
            # 'CLOSESPIDER_PAGECOUNT': 0, #0,
            #
            # 'CONCURRENT_REQUESTS': 500, #25
            # 'CONCURRENT_REQUESTS_PER_DOMAIN': 500, #50
            # 'CONCURRENT_REQUESTS_PER_IP': 500, #50
            # 'RANDOMIZE_DOWNLOAD_DELAY': 0,
            #
            #
            # 'REACTOR_THREADPOOL_MAXSIZE': 20,
            'COOKIES_ENABLED': False,
            # 'RETRY_ENABLED': True, #False,
            # 'DOWNLOAD_TIMEOUT':  15, #15,
            # 'REDIRECT_ENABLED': False,

            # Concurrency Settings 2

            'CONCURRENT_REQUESTS': 25, #1000, #25
            'CONCURRENT_REQUESTS_PER_DOMAIN': 1, #1000, #50
            'CONCURRENT_REQUESTS_PER_IP': 25, # 1000, #50
            #'RANDOMIZE_DOWNLOAD_DELAY': 1,
            'DOWNLOAD_DELAY': 2,
            'RETRY_HTTP_CODES' : [403], # add here any status codes you receive when getting banned
            'RETRY_TIMES' : 10

            # Output Settings
            #'FEEDS': {
            #    'outputs/output.json': {'format': 'jsonlines'},
            #},

        }
