import configparser

from elasticsearch6 import Elasticsearch

Config = configparser.ConfigParser()
Config.read("config.ini")
esClient: Elasticsearch = None
ES_ENABLED = False
INDEX = "mdx_examples_index"

if Config["ES"]["Enable"] == "true":
    esClient = Elasticsearch([{'host': Config["ES"]["Host"], 'port': Config["ES"]["Port"]}])
    try:
        if esClient.ping():
            ES_ENABLED = True
    except:
        ES_ENABLED = False
