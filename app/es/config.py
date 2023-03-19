import logging
from enum import unique, Enum

from elasticsearch7 import Elasticsearch

from app.config import es_config

log = logging.getLogger(__name__)

esClient = None

if es_config.enable:
    esClient = Elasticsearch([{'host': es_config.host, 'port': es_config.port}])
    try:
        if esClient.ping():
            log.info(">>>connected ES...")
    except:
        log.error(">>>try connect to ES failed, disabled ES...")


@unique
class ESConst(str, Enum):
    """
    es index name and mapping fields name
    """
    index = "mdict_examples_index"
    word = "word"
    example_en = "en"
    example_zh = "zh"
    example_html = "html"
    dictionary = "dictionary"
