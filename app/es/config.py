import dataclasses
import json
import logging

from elasticsearch7 import Elasticsearch

from app.config import es_config

log = logging.getLogger(__name__)

esClient = None

if es_config.enable:
    esClient = Elasticsearch([{'host': es_config.host, 'port': es_config.port}])
    try:
        if esClient.ping():
            log.info(">>>connected ES...")
    except Exception as e:
        log.error(">>>try connect to ES failed, disabled ES...")
        logging.exception(e)


class ESConst:
    """
    es index name and mapping fields name
    """
    index = "mdict_examples_index"
    word = "word"
    example_en = "en"
    example_zh = "zh"
    example_html = "html"
    dictionary = "dictionary"
    batch_size = 3000


@dataclasses.dataclass
class ESDoc:
    dictionary: str
    word: str
    en: str
    zh: str
    html: str

    @property
    def json(self):
        return json.dumps(self.__dict__)
