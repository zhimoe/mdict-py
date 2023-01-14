# -*- coding: utf-8 -*-

import logging
import os

from mdict.mdict_db import MdictDb

log = logging.getLogger("Mdict")
logging.basicConfig(level=logging.INFO)

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
    MdxIndexBuilders[name] = MdictDb(location)

log.info(f">>>all dictionaries= {MdxDicts} are indexed")
