import logging

import src.es.config as config
from src.config import es_config
from src.es.config import ExampleConst
from src.es.indexing import es_indexing
from src.mdict import MdictDbMap

log = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

if es_config.enable:
    log.info(">>>ES enabled, starting indexing the LSC4 examples to es...")
    es_indexing(MdictDbMap['LSC4'])
else:
    log.info(">>>ES disabled, indexing skipped...")


def search_examples(word: str, lang: str) -> str:
    if not es_config.enable:
        return ""

    dsl = {
        "query": {
            "match": {
                lang: word
            }
        }
    }
    res = config.esClient.search(index=ExampleConst.index, body=dsl)
    examples_html = """ <br/>
                        <strong>朗文当代4相关例句</strong>
                        <link rel="stylesheet" type="text/css" href="LSC4.css">
                    """
    if res["hits"]["total"]["value"] > 0:
        hits = res["hits"]["hits"]
        for hit in hits:
            one_example_html = hit["_source"][ExampleConst.example_html]
            examples_html += '<span class="example">' + one_example_html + '</span>'
        return examples_html
    return ''


def search_zh_examples(word: str) -> str:
    """
    查询es中朗文4的example
    """
    return search_examples(word, "zh")


def search_en_examples(word: str) -> str:
    return search_examples(word, "en")
