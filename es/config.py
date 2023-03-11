import configparser
import logging

from elasticsearch7 import Elasticsearch

log = logging.getLogger("ES")
logging.basicConfig(level=logging.INFO)

Config = configparser.ConfigParser()
Config.read("config.ini")
global esClient
ES_ENABLED = False
INDEX = "mdx_examples_index"

if Config["ES"]["Enable"] == "Y":
    esClient = Elasticsearch([{'host': Config["ES"]["Host"], 'port': Config["ES"]["Port"]}])
    try:
        if esClient.ping():
            ES_ENABLED = True
            log.info(">>>connected ES...")
    except:
        log.error(">>>try connect to ES failed, disabled ES...")
        ES_ENABLED = False
