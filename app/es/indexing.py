import logging
import sqlite3
from typing import List

from bs4 import BeautifulSoup
from elasticsearch7 import helpers

from app.es.client import ESConst, ESDoc
from app.mdict import MdictDbMap

log = logging.getLogger(__name__)


def indexing(client, dicts: List[str]) -> int:
    """indexing all examples in mdx dict"""
    # create index
    if not _create_index(client):
        return 0
    log.info(">>>ES enabled, starting indexing the examples to es...")
    for d in dicts:
        _es_indexing(d, MdictDbMap[d])


def _es_indexing(client, dictionary, mdictdb) -> int:
    """indexing all examples in mdx dict
    TODO: 性能很差，indexing动作应该放在解析mdx文件的时候
    :param dictionary LSC4 or O8C
    :param mdictdb dictionary sqlite3 db metadata
    """
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
        examples.extend(exs)
        if len(examples) > ESConst.batch_size:
            _ingest(examples)
            examples.clear()
    _ingest(examples)
    log.info(f">>>indexing {dictionary} done, doc count={len(keys)}")


def _ingest(client, examples: List[ESDoc]) -> int:
    """
    将例句写入到ES中，字段（id,word,en,zh,html).
    搜索的是en,zh字段，id=word+en.strip保证例句不重复
    html是例句的原始html，方便展示
    :param examples: List[ESDoc]
    :return: success count
    """
    # if len(examples) > ESConst.batch_size + 1:
    #     print(f">>>too many docs input one time, try to split into small size less than {ESConst.batch_size}")
    #     return 0
    docs = []
    for doc in examples:
        body = {
            "_index": ESConst.index,
            "_source": doc.json,
        }
        docs.append(body)
    helpers.bulk(client, docs)
    return len(examples)


def _example_parse(dictionary: str, word: str, raw_html: str) -> List[ESDoc]:
    """
    TODO: 如何实现类似java多态的调用
    """
    result = []
    if not raw_html:
        return result
    bs = BeautifulSoup(raw_html, "html.parser")
    if dictionary == "O8C":
        examples = bs.find_all("span", attrs={"level": "4", "class": "x-g"})
        for example in examples:
            try:
                en = example.find("span", attrs={"level": "5", "class": "x"})
                zh = example.find("span", attrs={"level": "5", "class": "tx"})
                if en and zh:
                    result.append(
                        ESDoc(
                            dictionary,
                            word,
                            en.text,
                            zh.text,
                            example.encode_contents().decode(),
                        )
                    )
            except Exception as e:
                logging.exception(e, exc_info=True)
                logging.info(f">>>parse failed, element: {example}")
    if dictionary == "LSC4":
        examples = bs.find_all("span", attrs={"class": "example"})
        for example in examples:
            try:
                en = example.next.text
                zh = example.next.nextSibling.text
                result.append(
                    ESDoc(dictionary, word, en, zh, example.encode_contents().decode())
                )
            except AttributeError:
                if example.has_attr("toolskip"):
                    en = example.text
                    zh = example.text
                    result.append(
                        ESDoc(
                            dictionary, word, en, zh, example.encode_contents().decode()
                        )
                    )
                else:
                    log.info(f">>>parse failed, element: {example}")
    return result


def _create_index(client) -> bool:
    """创建index"""
    if client.indices.exists(ESConst.index):
        log.info(f">>>the index {ESConst.index} already exists,indexing skipped")
        return False
    mapping = {
        "settings": {
            "index": {"number_of_shards": 1, "number_of_replicas": 1},
            "analysis": {
                "analyzer": {
                    "default": {"type": "standard"},
                    "default_search": {"type": "standard"},
                }
            },
        },
        "mappings": {
            "properties": {
                ESConst.dictionary: {"type": "keyword"},
                ESConst.word: {"type": "keyword"},
                ESConst.example_en: {"type": "text"},
                ESConst.example_zh: {"type": "text"},
                ESConst.example_html: {"type": "text"},
            }
        },
    }

    resp = client.indices.create(index=ESConst.index, body=mapping)
    log.info(f">>>ES index={ESConst.index} and mapping created")
    return resp
