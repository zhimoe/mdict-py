# -*- coding: utf-8 -*-

import logging
import os

from mdx.mdict_query import IndexBuilder

MdxIndexBuilders = dict()

MdxDicts = {"LSC4": "./resources/mdx/LSC4.mdx",
            "O8C": "./resources/mdx/O8C.mdx",
            "hycd_3rd": "./resources/mdx/hycd_3rd.mdx"}

for name, location in MdxDicts.items():
    if not os.path.exists(location):
        logging.warning(f"the dict({name}) file:{location} doesn't exist, skipped")
        continue
    _builder = IndexBuilder(location)
    MdxIndexBuilders[name] = _builder
logging.info(f"all dictionaries= {MdxDicts}")
