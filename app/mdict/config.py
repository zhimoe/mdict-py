# -*- coding: utf-8 -*-

import logging
import os

from app.config import ROOT_DIR
from app.mdict.mdict_db import MdictDb

log = logging.getLogger("Mdict")
logging.basicConfig(level=logging.INFO)

MdictDbMap = dict()

MdxFiles = {
    "HAN3": f'{os.path.join(ROOT_DIR, "resources/mdx/zh/汉语词典3.mdx")}',
    "O8C": f'{os.path.join(ROOT_DIR, "resources/mdx/en/牛津高阶8.mdx")}',
    "LSC4": f'{os.path.join(ROOT_DIR, "resources/mdx/en/朗文当代4.mdx")}',
}

for name, location in MdxFiles.items():
    if not os.path.exists(location):
        log.warning(f"the dict({name}) file:{location} doesn't exist, skipped")
        continue
    MdictDbMap[name] = MdictDb(location)

if MdictDbMap:
    log.info(f">>>all MdictDbs are built, dictionaries= {MdxFiles}")
