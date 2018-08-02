# -*- coding: utf-8 -*-
"""
数据格式化工具
"""

import numpy as np

def is_chinese(word):
    """
    判断是否为中文字符
    """
    if word >= u'\u4e00' and word <= u'\u9fff':
        return True
    else:
        return False


def word_counter(file_data):
    """
    get word count
    中文字算一个字
    是之前是字母且后一个不是字母算一个单词
    """
    count = 0
    is_word = False
    for char in file_data:
        if char.isalpha():
            is_word = True
            continue
        if is_word:
            count += 1
            is_word = False
        if is_chinese(char):
            count += 1
    return count


def paragraph_counter(file_data):
    """
    get paragraph count
    由于解析出来的文本会有很多无意义的回车
    所以使用[句号回车]结尾的标注为一段
    """
    if file_data.count('。\n') > 0:
        return file_data.count('。\n')
    else:
        return file_data.count('.\n')


def find_time(file_data, start):
    """
    获取参考文献发表年限
    由于文献的排版问题，会导致文件序号和发表年限无法对应
    但总的年限集合数据不会有问题
    暂时会有个别年份匹配错误，还未解决 正确率90%
    """
    year = 0
    year_location = 200000000
    for i in range(1990, 2019):
        location = file_data.find(str(i), start, start+20000)
        if location != -1 and location < year_location:
            year_location = location
            year = i
    return year


def reference_counter(file_data):
    """
    get reference data
    由\n[1]或\n［1］来判定参考文件
    """
    counter = 1
    years = []
    while True:
        start1 = file_data.rfind('\n['+str(counter)+']')
        start2 = file_data.rfind('\n['+str(counter)+' ]')
        start3 = file_data.rfind('\n［'+str(counter)+'］')
        start4 = file_data.rfind('\n［'+str(counter)+' ］')
        start = np.amax([start1, start2, start3, start4])
        if start > 0:
            years.append(find_time(file_data, start))
            counter += 1
            continue
        break
    return {"counter": counter, "years": years}


def publish_date(file_data):
    """
    get publish data
    从文章头部开始查找最先出现的年份
    """
    year = 0
    publish_year_location = 200000000
    for i in range(1800, 2019):
        location = file_data.find(str(i), 0, 20000)
        if location != -1 and location < publish_year_location:
            publish_year_location = location
            year = i
    return year


def out_of_date(_publish_year, reference_years):
    """
    参考文献过时程度
    发表论文年限-参考文献发表年限
    """
    times = []
    for year in reference_years:
        times.append(_publish_year-year)
    return times
