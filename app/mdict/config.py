# -*- coding: utf-8 -*-

import logging
import os
from typing import Dict

from app.config import file_abspath
from app.mdict.mdict_db import MdictDb

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def init_mdict_map(dicts_map: Dict):
    MdxFiles = {
        "HAN3": file_abspath("resources/mdx/zh/汉语词典3.mdx"),
        "O8C": file_abspath("resources/mdx/en/牛津高阶8.mdx"),
        "LSC4": file_abspath("resources/mdx/en/朗文当代4.mdx"),
    }

    for name, location in MdxFiles.items():
        if os.path.exists(location):
            dicts_map[name] = MdictDb(location)
        else:
            log.warning(f"the dict({name}) file:{location} doesn't exist, skipped")
    if not dicts_map:
        log.error("all mdict files are not exist, please check the file location.")


MdictDbMap = dict()
init_mdict_map(MdictDbMap)
