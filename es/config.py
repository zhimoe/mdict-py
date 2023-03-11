import configparser
import logging
from enum import unique, Enum

from elasticsearch7 import Elasticsearch

log = logging.getLogger("ES")
logging.basicConfig(level=logging.INFO)

Config = configparser.ConfigParser()
Config.read("config.ini")
global esClient
ES_ENABLED = False

if Config["ES"]["Enable"] == "Y":
    esClient = Elasticsearch([{'host': Config["ES"]["Host"], 'port': Config["ES"]["Port"]}])
    try:
        if esClient.ping():
            ES_ENABLED = True
            log.info(">>>connected ES...")
    except:
        log.error(">>>try connect to ES failed, disabled ES...")
        ES_ENABLED = False


@unique
class ExampleConst(str, Enum):
    """
    es index name and mapping fields name
    """
    index = "mdict_examples_index"
    example_en = "en"
    example_zh = "zh"
    example_html = "html"
    dictionary = "dictionary"
