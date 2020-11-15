# -*- coding: utf-8 -*-
# version: python 3.5
import os
import io
import re
from typing import Dict, Any


def read_all_lines(path) -> str:
    """读取文本文件返回一行string"""
    line_str = ''
    with io.open(path, 'r', -1, 'utf-8') as f:
        for line in f:
            line_str += line
    return line_str


def read_all_bytes(path) -> bytes:
    """读取二进制文件（byte）"""
    all_bytes = b''
    with io.open(path, 'br') as f:
        for line in f:
            all_bytes += line
    return all_bytes


def get_file_ext(path) -> str:
    """得到文件后缀（不包含点）"""
    return os.path.splitext(path)[1][1:]


def get_filename(path) -> str:
    """/code/file.py -> file.py"""
    return os.path.basename(path)


def match_file_ext(path, ext) -> bool:
    """判断是否指定后缀文件,ext不包含点"""
    if get_file_ext(path) == ext:
        return True
    else:
        return False


def path_exists(path) -> bool:
    """判断文件或目录是否存在"""
    return os.path.exists(path)


def del_file(path) -> bool:
    """删除文件"""
    if path_exists(path):
        os.remove(path)
        return True
    else:
        return False


def get_all_files(root_dir) -> list:
    """得到指定路径所有文件,递归获取子文件"""
    files = []
    if path_exists(root_dir):
        for lists in os.listdir(root_dir):
            path = os.path.join(root_dir, lists)
            if os.path.isdir(path):
                get_all_files(path)
            if os.path.isfile(path):
                files.append(path)
    return files


def del_file_by_ext(path, ext) -> None:
    """删除所有指定目录下指定后缀（不加点）文件"""
    if (path is None) or (len(path.strip()) <= 0):
        return
    if (ext is None) or (len(ext.strip()) <= 0):
        return
    all_file = get_all_files(path)
    for f in all_file:
        if match_file_ext(f, ext):
            del_file(f)


def get_static_map(resource_path, content_type_map) -> Dict[str, Any]:
    """将static目录下面的文件名全部收集，return {filename:filepath}"""
    result = {}
    files = get_all_files(resource_path)
    for p in files:
        if get_file_ext(p) in content_type_map:
            p = p.replace('\\', '/')
            result[re.match('.*?/static(/.*)', p).groups()[0]] = p
    return result


def is_chinese(word) -> bool:
    """判断是否是中文字符串
    :param word
    :return bool
    """
    for ch in word:
        if not u'\u4e00' <= ch <= u'\u9fff':
            return False
    return True
