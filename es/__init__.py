import es.config as config
from es.indexing import es_indexing
from mdict import MdxIndexBuilders

import logging

log = logging.getLogger("ES")
logging.basicConfig(level=logging.INFO)

if config.ES_ENABLED:
    log.info(">>>ES enabled, starting indexing the LSC4 chinese examples to es...")
    es_indexing(MdxIndexBuilders['LSC4'])
else:
    log.info(">>>ES disabled, indexing skipped...")


def search_han_examples(word: str) -> str:
    """查询es中朗文4的example
    """
    if not config.ES_ENABLED:
        return ""

    dsl = {
        "query": {
            "match": {
                "han": word
            }
        }
    }
    res = config.esClient.search(index=config.INDEX, body=dsl)
    examples_html = """<strong>朗文当代4相关例句</strong><link rel="stylesheet" type="text/css" href="LSC4.css">"""
    if res["hits"]["total"]["value"] > 0:
        hits = res["hits"]["hits"]
        for hit in hits:
            one_example_html = hit["_source"]["templates"]
            examples_html += '<span class="example">' + one_example_html + '</span>'
        return examples_html
    return ''
