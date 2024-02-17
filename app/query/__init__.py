import logging

from app.es import search_zh_examples, search_en_examples
from app.mdict import get_definition_mdx

log = logging.getLogger(__name__)


def qry_mdx_def(text: str) -> str:
    """
    :param text:
    :return:
    """
    if not text:
        return ""
    if _contains_chinese(text):
        resp = ""
        try:
            resp += search_zh_examples(text)
        except Exception as e:
            logging.exception("search es examples failed", e)
        return get_definition_mdx(text, "HAN3") + resp

    resp = ""
    try:
        resp += search_en_examples(text)
    except Exception as e:
        logging.exception("search es examples failed", e)
    # multi words then only search examples
    if len(text.split(" ")) > 1:
        return resp
    # one word then search both dictionary and examples
    return get_definition_mdx(text, "O8C") + resp


def _contains_chinese(word: str) -> bool:
    """判断是否包含中文字符串，中英文混合判定为中文
    :param word
    :return bool
    """
    for ch in word:
        if "\u4e00" <= ch <= "\u9fff":
            return True
    return False
