# import logging
# import sqlite3
#
# from bs4 import BeautifulSoup
#
# from src.mdict import MdictDbMap
#
# if __name__ == '__main__':
#     mdcitdb = MdictDbMap['O8C']
#     conn = sqlite3.connect(mdcitdb.get_mdx_db())
#     cursor = conn.execute("SELECT key_text FROM MDX_INDEX")
#     keys = [item[0] for item in cursor]
#     conn.close()
#
#     examples = []
#     result = []
#
#     for key in keys:
#         content = mdcitdb.mdx_lookup(key)
#         str_content = ""
#         if len(content) > 0:
#             for c in content:
#                 str_content += c.replace("\r\n", "").replace("entry:/", "")
#         bs = BeautifulSoup(str_content, "html.parser")
#         examples = bs.find_all('span', attrs={"level": "4", "class": "x-g"})
#         for html in examples:
#             try:
#                 print(str_content.enco)
#                 # # print(html.text)
#                 # en = html.find('span', attrs={"level": "5", "class": "x"})
#                 # zh = html.find('span', attrs={"level": "5", "class": "tx"})
#                 # if en and zh:
#                 #     print(f">>>en {en.text}")
#                 #     print(f">>>en {zh.text}")
#             except Exception as e:
#                 logging.exception(e, exc_info=True)
#             # try:
#             #     en = html.next.text
#             #     zh = html.next.nextSibling.text
#             #     result.append((word, en, zh, html.encode_contents().decode()))
#             # except AttributeError:
#             #     if html.has_attr('toolskip'):
#             #         en = html.text
#             #         zh = html.text
#             #         result.append((word, en, zh, html.encode_contents().decode()))
#             #     else:
#             #         logging.info(f">>>wrong element: {html}")
