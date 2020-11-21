# -*- coding: utf-8 -*-
# version: python 3.5


import json
import os
import re
import sqlite3
import sys
import zlib  # zlib compression is used for engine version >=2.0
from struct import pack
import logging as log
from readmdict import MDX, MDD

# LZO compression is used for engine version < 2.0
try:
    import lzo
except ImportError:
    lzo = None
    print("LZO compression support is not available")

# 2x3 compatible
if sys.hexversion >= 0x03000000:
    unicode = str
log.getLogger("mdx_query")

version = '1.1'

if __name__ == '__main__':
    conn = sqlite3.connect("/home/zhimoe/code/mdict-py/LSC4.mdx.db")
    cursor = conn.execute('SELECT key_text FROM MDX_INDEX')
    keys = [item[0] for item in cursor]
    conn.close()
    print(len(keys))


def query_mdx_mdd_keys(conn, word):
    if word:
        if '*' in word:
            word = word.replace('*', '%')
        else:
            word = word + '%'
        cursor = conn.execute('SELECT key_text FROM MDX_INDEX WHERE key_text LIKE \"' + word + '\"')
        keys = [item[0] for item in cursor]
    else:
        cursor = conn.execute('SELECT key_text FROM MDX_INDEX')
        keys = [item[0] for item in cursor]
    conn.close()
    return keys


class IndexBuilder(object):
    """将mdx/mdd文件解析出来，单词和对应的解释内容在mdx文件中的偏移量记录到sqlite3数据库中
    查询时，则根据单词先到sqlite3获取到偏移量，然后读取文件。
    解析mdx的过程比较复杂，考虑到了不同版本mdx文件规范，目前不支持加密的mdx
    """

    # todo: enable history
    def __init__(self, file_name, encoding="", passcode=None, force_rebuild=False, enable_history=False, sql_index=True,
                 check=False):
        self._mdx_file = file_name
        self._mdd_file = ""
        self._encoding = ''
        self._stylesheet = {}
        self._title = ''
        self._version = ''
        self._description = ''
        self._sql_index = sql_index
        self._check = check
        _filename, _extension = os.path.splitext(file_name)
        assert (_extension == '.mdx')
        assert (os.path.isfile(file_name))
        self._mdx_db = _filename + ".mdx.db"
        # make index anyway
        if force_rebuild:
            self._make_mdx_index(self._mdx_db)
            # 如果有同名的mdd文件，也重建索引
            self._mdd_index(self, _filename)

        # if mdx.db exist, then init IndexBuilder from db
        if os.path.isfile(self._mdx_db):
            self._init_from_db(_filename)
        else:
            self._make_mdx_index(self._mdx_db)
        self._mdd_index(_filename)

    def _mdd_index(self, _filename):
        if os.path.isfile(_filename + ".mdd"):
            self._mdd_file = _filename + ".mdd"
            self._mdd_db = _filename + ".mdd.db"
            if not os.path.isfile(self._mdd_db):
                self._make_mdd_index(self._mdd_db)

    def _init_from_db(self, _filename: str):
        """init IndexBuilder from mdx.db file"""
        # read from META table
        conn = sqlite3.connect(self._mdx_db)
        cursor = conn.execute("SELECT * FROM META WHERE key = \"version\"")
        # 判断有无版本号
        for cc in cursor:
            self._version = cc[1]
        # if not version info
        if not self._version:
            print("version info not found")
            conn.close()
            self._make_mdx_index(self._mdx_db)
            print("mdx.db rebuilt!")
            if os.path.isfile(_filename + '.mdd'):
                self._mdd_file = _filename + ".mdd"
                self._mdd_db = _filename + ".mdd.db"
                self._make_mdd_index(self._mdd_db)
                print("mdd.db rebuilt!")
        cursor = conn.execute("SELECT * FROM META WHERE key = \"encoding\"")
        for cc in cursor:
            self._encoding = cc[1]
        cursor = conn.execute("SELECT * FROM META WHERE key = \"stylesheet\"")
        for cc in cursor:
            self._stylesheet = json.loads(cc[1])
        cursor = conn.execute("SELECT * FROM META WHERE key = \"title\"")
        for cc in cursor:
            self._title = cc[1]
        cursor = conn.execute("SELECT * FROM META WHERE key = \"description\"")
        for cc in cursor:
            self._description = cc[1]

    def _replace_stylesheet(self, txt):
        # substitute stylesheet definition
        txt_list = re.split('`\d+`', txt)
        txt_tag = re.findall('`\d+`', txt)
        txt_styled = txt_list[0]
        for j, p in enumerate(txt_list[1:]):
            style = self._stylesheet[txt_tag[j][1:-1]]
            if p and p[-1] == '\n':
                txt_styled = txt_styled + style[0] + p.rstrip() + style[1] + '\r\n'
            else:
                txt_styled = txt_styled + style[0] + p + style[1]
        return txt_styled

    def _make_mdx_index(self, db_name):
        if os.path.exists(db_name):
            os.remove(db_name)
        mdx = MDX(self._mdx_file)
        self._mdx_db = db_name
        returned_index = mdx.get_index(check_block=self._check)
        index_list = returned_index['index_dict_list']
        print("db_name=" + db_name)
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute(
            ''' CREATE TABLE MDX_INDEX
               (key_text text not null,
                file_pos integer,
                compressed_size integer,
                decompressed_size integer,
                record_block_type integer,
                record_start integer,
                record_end integer,
                offset integer
                )'''
        )

        tuple_list = [
            (item['key_text'],
             item['file_pos'],
             item['compressed_size'],
             item['decompressed_size'],
             item['record_block_type'],
             item['record_start'],
             item['record_end'],
             item['offset']
             )
            for item in index_list
        ]
        c.executemany('INSERT INTO MDX_INDEX VALUES (?,?,?,?,?,?,?,?)',
                      tuple_list)
        # build the metadata table
        meta = returned_index['meta']
        c.execute(
            '''CREATE TABLE META
               (key text,
                value text
                )''')

        c.executemany(
            'INSERT INTO META VALUES (?,?)',
            [('encoding', meta['encoding']),
             ('stylesheet', meta['stylesheet']),
             ('title', meta['title']),
             ('description', meta['description']),
             ('version', version)
             ]
        )

        if self._sql_index:
            c.execute('''
                CREATE INDEX key_index ON MDX_INDEX (key_text)
                ''')

        conn.commit()
        conn.close()
        # set class member
        self._encoding = meta['encoding']
        self._stylesheet = json.loads(meta['stylesheet'])
        self._title = meta['title']
        self._description = meta['description']

    def _make_mdd_index(self, db_name):
        if os.path.exists(db_name):
            os.remove(db_name)
        mdd = MDD(self._mdd_file)
        self._mdd_db = db_name
        index_list = mdd.get_index(check_block=self._check)
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute(
            ''' CREATE TABLE MDX_INDEX
               (key_text text not null unique,
                file_pos integer,
                compressed_size integer,
                decompressed_size integer,
                record_block_type integer,
                record_start integer,
                record_end integer,
                offset integer
                )'''
        )

        tuple_list = [
            (item['key_text'],
             item['file_pos'],
             item['compressed_size'],
             item['decompressed_size'],
             item['record_block_type'],
             item['record_start'],
             item['record_end'],
             item['offset']
             )
            for item in index_list
        ]
        c.executemany('INSERT INTO MDX_INDEX VALUES (?,?,?,?,?,?,?,?)',
                      tuple_list)
        if self._sql_index:
            c.execute(
                '''
                CREATE UNIQUE INDEX key_index ON MDX_INDEX (key_text)
                '''
            )

        conn.commit()
        conn.close()

    def get_mdx_by_index(self, fmdx, index):
        record = self.get_record_by_index(fmdx, index)
        record = record.decode(self._encoding, errors='ignore').strip(u'\x00').encode('utf-8')
        if self._stylesheet:
            record = self._replace_stylesheet(record)
        record = record.decode('utf-8')
        return record

    def get_record_by_index(self, fmdx, index):
        fmdx.seek(index['file_pos'])
        record_block_compressed = fmdx.read(index['compressed_size'])
        record_block_type = record_block_compressed[:4]
        record_block_type = index['record_block_type']
        decompressed_size = index['decompressed_size']
        # adler32 = unpack('>I', record_block_compressed[4:8])[0]
        if record_block_type == 0:
            _record_block = record_block_compressed[8:]
            # lzo compression
        elif record_block_type == 1:
            if lzo is None:
                print("LZO compression is not supported")
                # decompress
            header = b'\xf0' + pack('>I', index['decompressed_size'])
            _record_block = lzo.decompress(record_block_compressed[8:], initSize=decompressed_size, blockSize=1308672)
            # zlib compression
        elif record_block_type == 2:
            # decompress
            _record_block = zlib.decompress(record_block_compressed[8:])
        record = _record_block[index['record_start'] - index['offset']:index['record_end'] - index['offset']]
        return record

    def get_mdd_by_index(self, fmdx, index):
        data = self.get_record_by_index(fmdx, index)
        return data

    def mdx_lookup(self, keyword):
        conn = sqlite3.connect(self._mdx_db)
        cursor = conn.execute("SELECT * FROM MDX_INDEX WHERE key_text = " + "\"" + keyword + "\"")
        lookup_result_list = []
        mdx_file = open(self._mdx_file, 'rb')
        for result in cursor:
            index = {'file_pos': result[1],
                     'compressed_size': result[2],
                     'decompressed_size': result[3],
                     'record_block_type': result[4],
                     'record_start': result[5],
                     'record_end': result[6],
                     'offset': result[7]}
            lookup_result_list.append(self.get_mdx_by_index(mdx_file, index))
        conn.close()
        mdx_file.close()
        return lookup_result_list

    def mdd_lookup(self, keyword):
        conn = sqlite3.connect(self._mdd_db)
        cursor = conn.execute("SELECT * FROM MDX_INDEX WHERE key_text = " + "\"" + keyword + "\"")
        lookup_result_list = []
        mdd_file = open(self._mdd_file, 'rb')
        for result in cursor:
            index = {'file_pos': result[1],
                     'compressed_size': result[2],
                     'decompressed_size': result[3],
                     'record_block_type': result[4],
                     'record_start': result[5],
                     'record_end': result[6],
                     'offset': result[7]}
            lookup_result_list.append(self.get_mdd_by_index(mdd_file, index))
        mdd_file.close()
        conn.close()
        return lookup_result_list

    def get_mdd_keys(self, query=''):
        if not self._mdd_db:
            return []
        conn = sqlite3.connect(self._mdd_db)
        return query_mdx_mdd_keys(conn, query)

    def get_mdx_keys(self, query=''):
        conn = sqlite3.connect(self._mdx_db)
        return query_mdx_mdd_keys(conn, query)

    def get_mdx_db(self):
        return self._mdx_db

# mdx_builder = IndexBuilder("oald.mdx")
# text = mdx_builder.mdx_lookup('dedication')
# keys = mdx_builder.get_mdx_keys()
# keys1 = mdx_builder.get_mdx_keys('abstrac')
# keys2 = mdx_builder.get_mdx_keys('*tion')
# for key in keys2:
# text = mdx_builder.mdx_lookup(key)[0]
# pass
