import configparser

from ai.translate import Translator

translator = Translator("data")

Config = configparser.ConfigParser()
Config.read("config.ini")


def get_prediction(text: str, source: str, target: str):
    """
    翻译内容, 英->中，如果输入的是中文，会出现返回长串的"一一一一一一一一一"
    :param text: 文本
    :param source: en、zh
    :param target: en、zh
    :return:
    """
    #
    if Config["AI"]["Enable"] == "false":
        return ""
    translation = translator.translate(source, target, text)
    if translation:
        return str(translation[0])
