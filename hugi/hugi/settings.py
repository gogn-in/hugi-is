# -*- coding: utf-8 -*-

import os

BOT_NAME = 'hugi'

LOG_LEVEL = "INFO"
SPIDER_MODULES = ['hugi.spiders']
NEWSPIDER_MODULE = 'hugi.spiders'
TELNETCONSOLE_ENABLED = False

SPIDER_MIDDLEWARES = {
                    'hugi.middlewares.deltafetch.DeltaFetch': 543,
                     }

DELTAFETCH_ENABLED = True
DELTAFETCH_DIR = os.path.abspath(os.path.dirname(__file__)).replace('\\', '/')
DELTAFETCH_RESET = False

ITEM_PIPELINES = {
   'hugi.pipelines.HugiUserPipeline': 300,
   'hugi.pipelines.HugiArticlePipeline': 400,
}

DATA_DIR = "data"

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY=3
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 32
# CONCURRENT_REQUESTS_PER_IP=16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False
