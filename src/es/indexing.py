import logging
import re
import sqlite3
from typing import Tuple, List

from bs4 import BeautifulSoup
from elasticsearch7 import helpers

from src.es.config import ExampleConst
from src.es.config import esClient
from src.mdict import MdictDbMap

log = logging.getLogger(__name__)


def example_parse_o8c(dict_name: str, word: str, html: str) -> Tuple[str, str, str]:
    """牛津8词典"""
    ...


def example_parse_lsc4(word: str, html: str) -> List[Tuple[str, str, str, str]]:
    """朗文4词典
    :return:(word,en,zh,templates)
    """
    result = []
    if not html:
        return result

    bs = BeautifulSoup(html, "html.parser")
    examples = bs.find_all('span', attrs={'class': "example"})
    for html in examples:
        try:
            en = html.next.text
            zh = html.next.nextSibling.text
            result.append((word, en, zh, html.encode_contents().decode()))
        except AttributeError:
            if html.has_attr('toolskip'):
                en = html.text
                zh = html.text
                result.append((word, en, zh, html.encode_contents().decode()))
            else:
                log.info(f">>>wrong element: {html}")
    return result


def ingest(dictionary: str, examples: List[Tuple[str, str, str, str]]) -> int:
    """
    将例句写入到ES中，字段（id,word,en,zh,html).
    搜索的是en,zh字段，id=word+en.strip保证例句不重复
    html是例句的原始html，方便展示
    :param dictionary: LSC4 or O8C,方便在返回html中添加css
    :param examples:(word,en,zh,html)
    :return: success count
    """

    docs = []
    for tpl in examples:
        word, en, zh, html = tpl
        source = {
            ExampleConst.dictionary: dictionary,
            ExampleConst.example_en: en,
            ExampleConst.example_zh: zh,
            ExampleConst.example_html: html
        }
        body = {
            "_index": ExampleConst.index,
            "_source": source,
            "_id": dictionary + "-" + word + "-" + re.sub(r'\W+', '', en)
        }
        docs.append(body)
    helpers.bulk(esClient, docs)
    return len(examples)


def es_indexing(mdcitdb) -> int:
    """indexing all examples in lsc4 dict
    TODO: 性能很差，indexing动作应该放在解析mdx文件的时候
    :param mdcitdb dictionary sqlite3 db metadata
    """
    # create index
    if not create_index():
        return 0
    log.info("es is connected and index created succeed, starting indexing...")
    conn = sqlite3.connect(mdcitdb.get_mdx_db())
    cursor = conn.execute("SELECT key_text FROM MDX_INDEX")
    keys = [item[0] for item in cursor]
    conn.close()

    examples = []

    for key in keys:
        content = mdcitdb.mdx_lookup(key)
        str_content = ""
        if len(content) > 0:
            for c in content:
                str_content += c.replace("\r\n", "").replace("entry:/", "")
        exs = example_parse_lsc4(key, str_content)
        if exs:
            examples.extend(exs)
            if len(examples) > 2000:
                ingest("lsc4", examples)
                examples = []
    ingest("lsc4", examples)
    log.info(">>>indexing done", len(keys))


if __name__ == '__main__':
    es_indexing(MdictDbMap['O8C'])


def create_index() -> bool:
    """创建index"""
    if esClient.indices.exists(ExampleConst.index):
        log.info(f">>>the index {ExampleConst.index} already exists,indexing skipped")
        return False
    mapping = {
        "settings": {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 1
            },
            "analysis": {
                "analyzer": {
                    "default": {
                        "type": "standard"
                    },
                    "default_search": {
                        "type": "standard"
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                ExampleConst.dictionary: {
                    "type": "keyword"
                },
                ExampleConst.example_en: {
                    "type": "text"
                },
                ExampleConst.example_zh: {
                    "type": "text"
                },
                ExampleConst.example_html: {
                    "type": "text"
                }
            }
        }
    }

    resp = esClient.indices.create(index=ExampleConst.index, body=mapping)
    log.info(f">>>ES index={ExampleConst.index} mapping created")
    return resp
