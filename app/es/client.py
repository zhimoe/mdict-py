import dataclasses
import json
import logging

from elasticsearch7 import Elasticsearch

from app.config import es_config

log = logging.getLogger(__name__)


def _singleton(c):
    """create a singleton instance"""
    return c()


@_singleton
class ESClient(object):
    def __init__(self):
        self.client = None
        if es_config.enable:
            self.client = Elasticsearch(
                [{"host": es_config.host, "port": es_config.port}]
            )
            try:
                if self.client.ping():
                    log.info(">>>connected ES...")
            except Exception as e:
                log.error(">>>try connect to ES failed, disabled ES...")
                logging.exception(e)
        else:
            log.error(
                ">>>create es client instance failed, please check the configuration."
            )

    def get_instance(self):
        """get es client instance"""
        return self.client


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
