# -*- coding: utf-8 -*-

import logging
import os
import re
import sys
from typing import List

import inflect
from spellchecker import SpellChecker

from es import search_han_examples
from mdx.mdict_query import IndexBuilder
from file_utils import is_chinese, get_all_files, match_file_ext, read_all_lines

BUILDERS = dict()

DICTS_MAP = {"LSC4": "./resources/mdx/LSC4.mdx",
             "O8C": "./resources/mdx/O8C.mdx",
             "hycd_3rd": "./resources/mdx/hycd_3rd.mdx"}


def build_dict():
    """将所有词典构建好builders,根据前端选择查询对应的词典"""
    global BUILDERS
    for d, f in DICTS_MAP.items():
        if not os.path.exists(f):
            logging.warning(f"the dict({d}) file:{f} doesn't exist,removed")
    for d, f in DICTS_MAP.items():
        _builder = IndexBuilder(f)
        BUILDERS[d] = _builder
    logging.info(f"all dictionaries= {DICTS_MAP}")


def choose_dict(word, dict_option) -> str:
    """根据用户的输入单词和内容判断使用选择哪个单词"""
    option = "O8C"
    if dict_option:
        option = dict_option
    if is_chinese(word):
        option = "hycd_3rd"
    return option


error_msg = """
            <link rel="stylesheet" type="text/css" href="O8C.css">
            <span backup-class="unbox_header_1" class="th">
            系统异常，请稍后再试
            </span>"""

sing = inflect.engine()  # 单复数转换
spellchecker = SpellChecker()  # 拼写纠正


def plural2singular(plural) -> str:
    """return singular of the plural word, if the input is not plural then return input """
    singular = sing.singular_noun(plural)
    if not singular:
        return plural
    return singular


def get_definition_mdx(word: str, dict_builder: IndexBuilder) -> str:
    """根据关键字得到MDX词典的解释"""
    try:
        if not word:
            return ""
        word = word.lower()
        content = dict_builder.mdx_lookup(word)
        # 复数转为单数
        if len(content) < 1:
            content = dict_builder.mdx_lookup(plural2singular(word))
        if len(content) < 1:
            word = spellchecker.correction(word)
            content = dict_builder.mdx_lookup(word)
        if len(content) < 1:
            content = dict_builder.mdx_lookup(word.upper())
        if is_chinese(word):
            content += search_han_examples(word)
        if len(content) < 1:
            return ""
        pattern = re.compile(r"@@@LINK=([\w\s]*)")
        rst = pattern.match(content[0])
        if rst is not None:
            link = rst.group(1).strip()
            content = dict_builder.mdx_lookup(link)

        str_content = ""
        if len(content) > 0:
            for c in content:
                str_content += c.replace("\r\n", "").replace("entry:/", "")

        injection_html = ''
        try:
            base_path = os.path.dirname(sys.executable)
        except IOError:
            base_path = os.path.abspath("")

        resource_path = os.path.join(base_path, 'mdx')

        injection = get_all_files(resource_path)

        for p in injection:
            if match_file_ext(p, 'templates'):
                injection_html += read_all_lines(p)

        output_html = str_content + injection_html
        return output_html
    except:
        return error_msg


def get_definition_mdd(word: str, builder: IndexBuilder) -> List[str]:
    """根据关键字得到MDD词典的媒体 """
    word = word.replace("/", "\\")
    content = builder.mdd_lookup(word)
    if len(content) > 0:
        return [content[0]]
    else:
        return []
