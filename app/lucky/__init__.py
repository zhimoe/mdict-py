words_list = open("app/lucky/freq_words.txt").read().splitlines()

count = -1


def get_random_word() -> str:
    """
    试试手气, 随机抽取一个单词返回
    """
    global count
    count += 1
    return words_list[count % len(words_list)]
