from es import search_zh_examples
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
    else:  # 英文词典
        if len(text.split(' ')) > 1:
            text = text.split(' ')[0]
        return get_definition_mdx(text, '牛津高阶8')


def _contains_chinese(word: str) -> bool:
    """判断是否包含中文字符串，中英文混合判定为中文
    :param word
    :return bool
    """
    for ch in word:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False
