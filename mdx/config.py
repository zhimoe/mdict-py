# -*- coding: utf-8 -*-

import logging
import os

from mdx.mdict_query import IndexBuilder

MdxIndexBuilders = dict()

MdxDicts = {
    "牛津高阶8": "./resources/mdx/en/牛津高阶8.mdx",
    "汉语词典3": "./resources/mdx/zh/汉语词典3.mdx"
}

for name, location in MdxDicts.items():
    if not os.path.exists(location):
        logging.warning(f"the dict({name}) file:{location} doesn't exist, skipped")
        continue
    _builder = IndexBuilder(location)
    MdxIndexBuilders[name] = _builder
logging.info(f"all dictionaries= {MdxDicts}")
