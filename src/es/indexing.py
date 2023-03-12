import logging
import re
import sqlite3
from typing import Tuple, List

from bs4 import BeautifulSoup
from elasticsearch7 import helpers

from src.es.config import ESConst, esClient

log = logging.getLogger(__name__)


def _example_parse(dictionary: str, word: str, html: str) -> List[Tuple[str, str, str, str]]:
    """
    TODO: 如何实现类似java多态的调用
    """

    if dictionary == 'O8C':
        return _example_parse_o8c(word, html)
    if dictionary == 'LSC4':
        return _example_parse_lsc4(word, html)


def _example_parse_o8c(word: str, html: str) -> List[Tuple[str, str, str, str]]:
    """牛津8词典"""
    result = []
    if not html:
        return result
    bs = BeautifulSoup(html, "html.parser")
    examples = bs.find_all('span', attrs={"level": "4", "class": "x-g"})
    for example in examples:
        try:
            en = example.find('span', attrs={"level": "5", "class": "x"})
            zh = example.find('span', attrs={"level": "5", "class": "tx"})
            if en and zh:
                result.append((word, en, zh, example.encode_contents().decode()))
        except Exception as e:
            logging.exception(e, exc_info=True)
            logging.info(f">>>parse failed, element: {example}")
    return result


def _example_parse_lsc4(word: str, html: str) -> List[Tuple[str, str, str, str]]:
    """朗文4词典
    :return:(word,en,zh,templates)
    """
    result = []
    if not html:
        return result

    bs = BeautifulSoup(html, "html.parser")
    examples = bs.find_all('span', attrs={'class': "example"})
    for example in examples:
        try:
            en = example.next.text
            zh = example.next.nextSibling.text
            result.append((word, en, zh, example.encode_contents().decode()))
        except AttributeError:
            if example.has_attr('toolskip'):
                en = example.text
                zh = example.text
                result.append((word, en, zh, example.encode_contents().decode()))
            else:
                log.info(f">>>parse failed, element: {example}")
    return result


def _ingest(dictionary: str, examples: List[Tuple[str, str, str, str]]) -> int:
    """
    将例句写入到ES中，字段（id,word,en,zh,html).
    搜索的是en,zh字段，id=word+en.strip保证例句不重复
    html是例句的原始html，方便展示
    :param dictionary: LSC4 or O8C,方便在返回html中添加css
    :param examples:(word,en,zh,html)
    :return: success count
    """
    if len(examples) > 5000:
        print(f">>>too many docs input one time, try to split into small size less than 5000")
        return 0
    docs = []
    for example in examples:
        word, en, zh, html = example
        source = {
            ESConst.dictionary: dictionary,
            ESConst.word: word,
            ESConst.example_en: en,
            ESConst.example_zh: zh,
            ESConst.example_html: html,
        }
        body = {
            "_index": ESConst.index,
            "_source": source,
            "_id": dictionary + "-" + word + "-" + re.sub(r'\W+', '', en)
        }
        docs.append(body)
    helpers.bulk(esClient, docs)
    return len(examples)


def es_indexing(dictionary, mdictdb) -> int:
    """indexing all examples in lsc4 dict
    TODO: 性能很差，indexing动作应该放在解析mdx文件的时候
    :param mdictdb dictionary sqlite3 db metadata
    :param dictionary LSC4 or O8C
    """
    # create index
    if not _create_index():
        return 0
    log.info("es is connected and index created succeed, starting indexing...")
    conn = sqlite3.connect(mdictdb.get_mdx_db())
    cursor = conn.execute("SELECT key_text FROM MDX_INDEX")
    keys = [item[0] for item in cursor]
    conn.close()

    examples = []

    for word in keys:
        content = mdictdb.mdx_lookup(word)
        html = ""
        if len(content) > 0:
            for c in content:
                html += c.replace("\r\n", "").replace("entry:/", "")
        exs = _example_parse(dictionary, word, html)
        if exs:
            examples.extend(exs)
            if len(examples) > 2000:
                _ingest(dictionary, examples)
                examples = []
    _ingest(dictionary, examples)
    log.info(">>>indexing done", len(keys))


def _create_index() -> bool:
    """创建index"""
    if esClient.indices.exists(ESConst.index):
        log.info(f">>>the index {ESConst.index} already exists,indexing skipped")
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
                ESConst.dictionary: {
                    "type": "keyword"
                },
                ESConst.word: {
                    "type": "keyword"
                },
                ESConst.example_en: {
                    "type": "text"
                },
                ESConst.example_zh: {
                    "type": "text"
                },
                ESConst.example_html: {
                    "type": "text"
                }
            }
        }
    }

    resp = esClient.indices.create(index=ESConst.index, body=mapping)
    log.info(f">>>ES index={ESConst.index} mapping created")
    return resp
