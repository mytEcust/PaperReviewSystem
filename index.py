# -*- coding: utf-8 -*-
"""
入口函数
"""

import os
import json
import textract
import numpy as np

PAPER_DIR = './paper_data/'
TRAIN_DIR = './train_data/'
FORMAT_DIR = './format_data/'


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
        if char >= u'\u4e00' and char <= u'\u9fff':
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


print("[START] switch paper to txt")
for paper in os.listdir(PAPER_DIR):
    text = textract.process(PAPER_DIR+paper)
    content = str(text, encoding="utf-8").strip()
    content = content.replace('\n\n', '\n')
    with open(TRAIN_DIR+paper.split(".")[0]+'.txt', 'w') as f:
        f.write(content)
print("[DONE] switch paper to txt")


print("[START] format paper")
for paper in os.listdir(TRAIN_DIR):
    with open(TRAIN_DIR+paper, 'r', encoding="utf-8") as f:
        f = f.read()
        FORMAT_OBJ = {}
        FORMAT_OBJ['words'] = word_counter(f)
        FORMAT_OBJ['paragraph'] = paragraph_counter(f)
        referenceObj = reference_counter(f)
        FORMAT_OBJ['reference_counter'] = referenceObj['counter']
        FORMAT_OBJ['reference_years'] = referenceObj['years']
        publish_year = publish_date(f)
        FORMAT_OBJ['publish_year'] = publish_year
        FORMAT_OBJ['out_of_date'] = out_of_date(
            publish_year, referenceObj['years'])
    with open(FORMAT_DIR+paper.split(".")[0]+'.json', 'w') as f_format:
        f_format.write(json.dumps(FORMAT_OBJ))
print("[DONE] format paper")
