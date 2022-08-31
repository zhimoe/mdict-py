# -*- coding: utf-8 -*-

import logging as log
import os

from mdx.index_builder import IndexBuilder

MdxIndexBuilders = dict()

MdxDicts = {
    "牛津高阶8": "./resources/mdx/en/牛津高阶8.mdx",
    "汉语词典3": "./resources/mdx/zh/汉语词典3.mdx",
    "LSC4": "./resources/mdx/en/LSC4.mdx",
}

for name, location in MdxDicts.items():
    if not os.path.exists(location):
        log.warning(f"the dict({name}) file:{location} doesn't exist, skipped")
        continue
    _builder = IndexBuilder(location)
    MdxIndexBuilders[name] = _builder
log.info(f"all dictionaries= {MdxDicts} are indexed")
