from es import search_han_examples
from ai import get_prediction
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
        return get_definition_mdx(text, 'hycd_3rd') + search_han_examples(text)
    else:  # 英文词典
        if len(text.split(' ')) > 1:
            text = text.split(' ')[0]
        return get_definition_mdx(text, 'O8C') + get_definition_mdx(text, 'LSC4')


def qry_ai_def(text: str) -> str:
    source, target = ("zh", "en") if contains_chinese(text) else ("en", "zh")
    return get_prediction(text, source, target)
