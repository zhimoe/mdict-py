import logging

import es.config as config
from es.config import ExampleConst
from es.indexing import es_indexing
from mdict import MdxIndexBuilders

log = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

if config.ES_ENABLED:
    log.info(">>>ES enabled, starting indexing the LSC4 examples to es...")
    es_indexing(MdxIndexBuilders['LSC4'])
else:
    log.info(">>>ES disabled, indexing skipped...")


def search_zh_examples(word: str) -> str:
    """查询es中朗文4的example
    """
    if not config.ES_ENABLED:
        return ""

    dsl = {
        "query": {
            "match": {
                "zh": word
            }
        }
    }
    res = config.esClient.search(index=ExampleConst.index, body=dsl)
    examples_html = """<strong>朗文当代4相关例句</strong><link rel="stylesheet" type="text/css" href="LSC4.css">"""
    if res["hits"]["total"]["value"] > 0:
        hits = res["hits"]["hits"]
        for hit in hits:
            one_example_html = hit["_source"][ExampleConst.example_html]
            examples_html += '<span class="example">' + one_example_html + '</span>'
        return examples_html
    return ''
