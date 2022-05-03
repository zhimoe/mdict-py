from es import search_han_examples
from mdx import get_definition_mdx
from file_utils import contains_chinese


def qry_mdx_def(text: str) -> str:
    """
    :param text:
    :return:
    """
    if not text:
        return ''
    if contains_chinese(text):
        return get_definition_mdx(text, '汉语词典3') + search_han_examples(text)
    else:  # 英文词典
        if len(text.split(' ')) > 1:
            text = text.split(' ')[0]
        return get_definition_mdx(text, '牛津高阶8')
