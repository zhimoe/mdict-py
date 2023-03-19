import logging

from app.config import es_config
from app.es.config import ESConst, esClient
from app.es.indexing import es_indexing
from app.mdict import MdictDbMap

log = logging.getLogger(__name__)

if es_config.enable:
    log.info(">>>ES enabled, starting indexing the LSC4 examples to es...")
    es_indexing('LSC4', MdictDbMap['LSC4'])
    es_indexing('O8C', MdictDbMap['O8C'])
else:
    log.info(">>>ES disabled, indexing skipped...")


def search_examples(word: str, lang: str) -> str:
    if not esClient:
        return ""

    dsl = {
        "query": {
            "match": {
                lang: word
            }
        }
    }
    res = esClient.search(index=ESConst.index, body=dsl)
    examples_html = """ <br/>
                        <strong>朗文当代4相关例句</strong>
                        <link rel="stylesheet" type="text/css" href="LSC4.css">
                    """
    if res["hits"]["total"]["value"] > 0:
        hits = res["hits"]["hits"]
        for hit in hits:
            one_example_html = hit["_source"][ESConst.example_html]
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
