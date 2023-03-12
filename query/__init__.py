from es import search_zh_examples, search_en_examples
from mdict import get_definition_mdx


def qry_mdx_def(text: str) -> str:
    """
    :param text:
    :return:
    """
    if not text:
        return ''
    if _contains_chinese(text):
        return get_definition_mdx(text, '汉语词典3') + search_zh_examples(text)

    # multi words then only search examples
    if len(text.split(' ')) > 1:
        return search_en_examples(text)
    # one word then search both dictionary and examples
    return get_definition_mdx(text, '牛津高阶8') + search_en_examples(text)


def _contains_chinese(word: str) -> bool:
    """判断是否包含中文字符串，中英文混合判定为中文
    :param word
    :return bool
    """
    for ch in word:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False
