import logging

from app.config import es_config
from app.es.client import ESConst, ESClient
from app.es.indexing import indexing

log = logging.getLogger(__name__)

esClient = ESClient.get_instance()

if es_config.enable:
    indexing(esClient, ["LSC4", "O8C"])
else:
    log.info(">>>ES disabled, indexing skipped...")


def search_examples(word: str, lang: str) -> str:
    if not esClient:
        return ""

    dsl = {"query": {"match": {lang: word}}}
    res = esClient.search(index=ESConst.index, body=dsl)
    examples_html = """ <br/>
                        <strong>牛津与朗文相关例句</strong>
                        <link rel="stylesheet" type="text/css" href="LSC4.css">
                    """
    if res["hits"]["total"]["value"] > 0:
        hits = res["hits"]["hits"]
        for hit in hits:
            one_example_html = hit["_source"][ESConst.example_html]
            examples_html += '<span class="example">' + one_example_html + "</span>"
        return examples_html
    return ""


def search_zh_examples(word: str) -> str:
    return search_examples(word, "zh")


def search_en_examples(word: str) -> str:
    return search_examples(word, "en")
