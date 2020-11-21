import re
import sqlite3
from typing import Tuple, List

from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch, helpers

from config import Config
from mdict_query import IndexBuilder

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
    except Exception:
        pass


def example_parse(dict: str, word: str, html: str) -> Tuple[str, str, str]:
    """
    从html中抽取出例句
    :param dict: which dictionary
    :param word: word
    :param html: explain of the word
    :return: tuple(word,en,han)
    """

    pass


def example_parse_o8c(dict: str, word: str, html: str) -> Tuple[str, str, str]:
    """牛津8词典"""
    pass


def example_parse_lsc4(dict: str, word: str, html: str) -> List[Tuple[str, str, str, str]]:
    """朗文4词典
    :return:(word,en,han,html)
    """
    result = []
    if not html:
        return result

    bs = BeautifulSoup(html, "html.parser")
    examples = bs.find_all('span', attrs={'class': "example"})
    for html in examples:
        try:
            en = html.next.text
            han = html.next.nextSibling.text
            result.append((word, en, han, html.encode_contents().decode()))
        except AttributeError:
            """some example has no next element"""
            pass
    return result


def ingest(dict: str, examples: List[Tuple[str, str, str, str]]) -> int:
    """
    将例句写入到ES中，字段（id,word,en,han,html).
    搜索的是en,han字段，id=word+en.strip保证例句不重复
    html是例句的原始html，方便展示
    :param dict: LSC4 or O8C,方便在返回html中添加css
    :param examples:(word,en,han,html)
    :return: success count
    """

    docs = []
    for tpl in examples:
        word, en, han, html = tpl
        source = {
            "dict": dict,
            "en": en,
            "han": han,
            "html": html
        }
        body = {
            "_index": INDEX,
            "_type": "doc",
            "_source": source,
            "_id": dict + "-" + word + "-" + re.sub(r'\W+', '', en)
        }
        docs.append(body)
    helpers.bulk(esClt, docs)
    print("bulk index finished")
    return len(examples)


def search(word: str) -> str:
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
    html = """<span>朗文4相关例句</span><link rel="stylesheet" type="text/css" href="LSC4.css">"""
    if res["hits"]["total"] > 0:
        hits = res["hits"]["hits"]
        for hit in hits:
            one_html = hit["_source"]["html"]
            html += '<span class="example">' + one_html + '</span>'
    return html


def indexing(builder: IndexBuilder) -> int:
    """indexing all examples in lsc4 dict
    TODO: 性能很差，indexing动作应该放在解析mdx文件的时候
    :param builder dict builder
    """
    if not USE_ES or not CONNECTED_ES:
        return 0

    # create index
    if not create_index():
        return 0
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
            if len(examples) > 100000:
                ingest("lsc4", examples)
                examples = []
    ingest("lsc4", examples)
    print("indexing done", len(keys))


def create_index() -> bool:
    """创建index"""
    if not CONNECTED_ES:
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
                    "html": {
                        "type": "text"
                    }
                }
            }
        }
    }

    return esClt.indices.create(index=INDEX, body=mappings)
