import configparser

from elasticsearch import Elasticsearch

Config = configparser.ConfigParser()
Config.read("config.ini")
esClt: Elasticsearch = None
ES_ENABLED = False
INDEX = "mdx_examples_index"

if Config["ES"]["Enable"] == "true":
    esClt = Elasticsearch([{'host': Config["ES"]["Host"], 'port': Config["ES"]["Port"]}])
    try:
        if esClt.ping():
            ES_ENABLED = True
    except:
        ES_ENABLED = False
