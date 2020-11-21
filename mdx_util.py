# -*- coding: utf-8 -*-
# version: python 3.5

import re
import sys
from typing import List

import inflect
from spellchecker import SpellChecker

from es import example_parse_lsc4, ingest, search
from file_util import *

not_found = """
            <link rel="stylesheet" type="text/css" href="O8C.css">
            <span backup-class="unbox_header_1" class="th">
            查无结果
            </span>
        """

sing = inflect.engine()
spellchecker = SpellChecker()


def plural2singular(plural) -> str:
    """return singular of the plural word, if the input is not plural then return input """
    singular = sing.singular_noun(plural)
    if not singular:
        return plural
    return singular


def get_definition_mdx(word, builder) -> List[bytes]:
    """根据关键字得到MDX词典的解释"""
    if not word:
        return [not_found.encode('utf-8')]
    word = word.lower()
    content = builder.mdx_lookup(word)
    if len(content) < 1:
        word = spellchecker.correction(word)
        content = builder.mdx_lookup(word)
    if len(content) < 1:
        content = builder.mdx_lookup(word.upper())
    if len(content) < 1:
        content = builder.mdx_lookup(plural2singular(word.lower()))
    if is_chinese(word):
        content += search(word)
    if len(content) < 1:
        return [not_found.encode('utf-8')]

    pattern = re.compile(r"@@@LINK=([\w\s]*)")
    rst = pattern.match(content[0])
    if rst is not None:
        link = rst.group(1).strip()
        content = builder.mdx_lookup(link)
    # remove \r\n and entry:/
    str_content = ""
    if len(content) > 0:
        for c in content:
            str_content += c.replace("\r\n", "").replace("entry:/", "")

    injection_html = ''
    try:
        base_path = os.path.dirname(sys.executable)
    except IOError:
        base_path = os.path.abspath(".")

    resource_path = os.path.join(base_path, 'mdx')

    injection = get_all_files(resource_path)

    for p in injection:
        if match_file_ext(p, 'html'):
            injection_html += read_all_lines(p)

    output_html = str_content + injection_html
    return [output_html.encode('utf-8')]


def get_definition_mdd(word, builder) -> List:
    """根据关键字得到MDD词典的媒体 """
    word = word.replace("/", "\\")
    content = builder.mdd_lookup(word)
    if len(content) > 0:
        return [content[0]]
    else:
        return []
