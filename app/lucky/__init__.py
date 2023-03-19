import random

words_list = open('app/lucky/freq_words.txt').read().splitlines()


def get_random_word() -> str:
    """
    试试手气, 随机抽取一个单词返回
    """
    return random.choice(words_list)
