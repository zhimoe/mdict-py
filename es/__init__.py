import re
import sqlite3
from typing import Tuple, List

from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch, helpers

from mdx.mdict_query import IndexBuilder

import configparser

Config = configparser.ConfigParser()
Config.read("config.ini")

INDEX = "mdx_examples_index"
USE_ES = False
CONNECTED_ES = False
# global es client
esClt = None

if Config["ES"]["Enable"] == "true":
    USE_ES = True
    esClt = Elasticsearch([{'host': Config["ES"]["Host"], 'port': Config["ES"]["Port"]}])
    try:
        if esClt.ping():
            CONNECTED_ES = True
    except:
        pass


def example_parse_o8c(dict_name: str, word: str, html: str) -> Tuple[str, str, str]:
    """牛津8词典"""
    pass


def example_parse_lsc4(dict_name: str, word: str, html: str) -> List[Tuple[str, str, str, str]]:
    """朗文4词典
    :return:(word,en,han,templates)
    """
    result = []
    if not html:
        return result

    bs = BeautifulSoup(html, "templates.parser")
    examples = bs.find_all('span', attrs={'class': "example"})
    for html in examples:
        try:
            en = html.next.text
            han = html.next.nextSibling.text
            result.append((word, en, han, html.encode_contents().decode()))
        except AttributeError:
            """some example has no next element"""
            print(f"this example is not on rule")
    return result


def ingest(dict_name: str, examples: List[Tuple[str, str, str, str]]) -> int:
    """
    将例句写入到ES中，字段（id,word,en,han,templates).
    搜索的是en,han字段，id=word+en.strip保证例句不重复
    html是例句的原始html，方便展示
    :param dict_name: LSC4 or O8C,方便在返回html中添加css
    :param examples:(word,en,han,templates)
    :return: success count
    """

    docs = []
    for tpl in examples:
        word, en, han, html = tpl
        source = {
            "dict": dict_name,
            "en": en,
            "han": han,
            "templates": html
        }
        body = {
            "_index": INDEX,
            "_type": "doc",
            "_source": source,
            "_id": dict_name + "-" + word + "-" + re.sub(r'\W+', '', en)
        }
        docs.append(body)
    helpers.bulk(esClt, docs)
    return len(examples)


def search_han_examples(word: str) -> str:
    """查询es中朗文4的example
    """
    if not USE_ES or not CONNECTED_ES:
        return ""

    dsl = {
        "query": {
            "match": {
                "han": word
            }
        }
    }
    res = esClt.search(index=INDEX, body=dsl)
    examples_html = """<strong>朗文4相关例句</strong><link rel="stylesheet" type="text/css" href="LSC4.css">"""
    if res["hits"]["total"] > 0:
        hits = res["hits"]["hits"]
        for hit in hits:
            one_example_html = hit["_source"]["templates"]
            examples_html += '<span class="example">' + one_example_html + '</span>'
    return examples_html


def es_indexing(builder: IndexBuilder) -> int:
    """indexing all examples in lsc4 dict
    TODO: 性能很差，indexing动作应该放在解析mdx文件的时候
    :param builder dict builder
    """
    if not USE_ES or not CONNECTED_ES:
        return 0

    # create index
    if not create_index():
        return 0
    print("es is connected and index created succeed, starting indexing the examples...")
    conn = sqlite3.connect(builder.get_mdx_db())
    cursor = conn.execute('SELECT key_text FROM MDX_INDEX')
    keys = [item[0] for item in cursor]
    conn.close()

    examples = []

    for key in keys:
        content = builder.mdx_lookup(key)
        str_content = ""
        if len(content) > 0:
            for c in content:
                str_content += c.replace("\r\n", "").replace("entry:/", "")
        exs = example_parse_lsc4("lsc4", key, str_content)
        if exs:
            examples.extend(exs)
            if len(examples) > 2000:
                ingest("lsc4", examples)
                examples = []
    ingest("lsc4", examples)
    print("indexing done", len(keys))


def create_index() -> bool:
    """创建index"""
    if not CONNECTED_ES:
        return False
    if esClt.indices.exists(INDEX):
        print(f"the index {INDEX} already exists,indexing skipped")
        return False
    mappings = {
        "settings": {
            "index": {
                "number_of_shards": 2,
                "number_of_replicas": 1
            },
            "analysis": {
                "analyzer": {
                    "default": {
                        "type": "ik_smart"
                    },
                    "default_search": {
                        "type": "ik_smart"
                    }
                }
            }
        },
        "mappings": {
            "doc": {
                "properties": {
                    "dict": {
                        "type": "keyword"
                    },
                    "en": {
                        "type": "text"
                    },
                    "han": {
                        "type": "text"
                    },
                    "templates": {
                        "type": "text"
                    }
                }
            }
        }
    }

    return esClt.indices.create(index=INDEX, body=mappings)
