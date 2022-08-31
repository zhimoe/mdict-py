import re
import sqlite3
from typing import Tuple, List

from bs4 import BeautifulSoup
from elasticsearch6 import helpers

from es.config import INDEX, esClient


def example_parse_o8c(dict_name: str, word: str, html: str) -> Tuple[str, str, str]:
    """牛津8词典"""
    ...


def example_parse_lsc4(word: str, html: str) -> List[Tuple[str, str, str, str]]:
    """朗文4词典
    :return:(word,en,han,templates)
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
    helpers.bulk(esClient, docs)
    return len(examples)


def es_indexing(builder) -> int:
    """indexing all examples in lsc4 dict
    TODO: 性能很差，indexing动作应该放在解析mdx文件的时候
    :param builder dict builder
    """
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
        exs = example_parse_lsc4(key, str_content)
        if exs:
            examples.extend(exs)
            if len(examples) > 2000:
                ingest("lsc4", examples)
                examples = []
    ingest("lsc4", examples)
    print("indexing done", len(keys))


def create_index() -> bool:
    """创建index"""
    if esClient.indices.exists(INDEX):
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

    return esClient.indices.create(index=INDEX, body=mappings)
