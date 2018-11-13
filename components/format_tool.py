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


def format_paper(file_data):
    """
    格式化文献，去除空格和换行
    """
    _file_data = file_data.replace(' ', '')
    _file_data = _file_data.replace('　', '')
    return _file_data.replace('\n', '')


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


def publish_data(file_data):
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


def search_start(file_data, start=0, end=1000, mark='('):
    """
    search start
    根据文献确定寻找作者单位信息的起始点
    """
    _start = start
    while 1:
        if _start < 0:
            return -1
        _start = file_data.find(mark, _start, end)
        has_chinese = False
        _count = 1  # 计数器
        while 1:
            if _count > 5:
                break
            has_chinese = has_chinese or is_chinese(file_data[_start+_count])
            if has_chinese:
                break
            _count += 1
        if has_chinese:
            return _start
        else:
            _start = file_data.find(mark, _start+1, end)


def find_institutions(file_data, start, end):
    """
    find institutions
    根据文献，开始标记，结束标记寻找作者单位信息
    """
    institutions = []
    _instit = ''
    if start < 0:
        return []
    while 1:
        if file_data[start] == ')' or file_data[start] == '）':
            return institutions
        elif is_chinese(file_data[start]):
            _instit = _instit+file_data[start]
        else:
            if len(_instit) > 0:
                if(len(_instit) > 4):
                    institutions.append(_instit)
                _instit = ''
        start += 1
        if(start > end):
            return institutions


def author_institutions_data(file_data):
    """
    get author data
    获取论文作者,及作者信息，简介
    90%左右的文献的作者单位信息都由()包含，故已此为标准进行截取
    并去除其中一些干扰信息
    剩余10%不到的文献没有作者单位信息，或者单位信息排版较为独特
    故不做多余的强耦合的获取方式
    """
    _start = 0
    while 1:
        if(_start > 500):
            return []
        start = search_start(file_data, _start, _start+1000, '(')
        end = start+1000
        institutions = find_institutions(file_data, start, end)
        if(len(institutions)):
            return institutions

        start = search_start(file_data, _start, _start+1000, '（')
        end = start+1000
        institutions = find_institutions(file_data, start, end)
        if(len(institutions)):
            return institutions

        _start += 100


def filter_authors(_authors):
    """
    过滤不合格的作者名字
    去除大于6个作者的作者们
    去除大于五个字的作者名字
    """
    if len(_authors) > 6:
        _authors = []
    _authors = [_auth for _auth in _authors if len(_auth) < 5]
    return _authors


def get_comma_authors(file_data, paper_title, first_author, institution):
    """
    获取全部作者
    情况1：以,分隔的作者，作者姓名间包含空格
    """
    _authors = []
    _author = ''
    _file_data = format_paper(file_data)
    # _file_data = file_data.replace(' ', '')
    # _file_data = _file_data.replace('\n', '')

    _authors_start = _file_data.find(first_author)
    if _authors_start > 1000:
        _authors_start = _file_data.find(paper_title)+len(paper_title)
    _authors_end = _file_data.find(institution, _authors_start)

    _authors_str = _file_data[_authors_start:_authors_end-1]
    _sentry = 0
    _space = 0
    while _sentry < len(_authors_str):
        if is_chinese(_authors_str[_sentry]):
            _author += _authors_str[_sentry]
            if _sentry == (len(_authors_str)-1):
                _authors.append(_author)
        elif _authors_str[_sentry] == ',' or _authors_str[_sentry] == '，' or _space > 0:
            if len(_author) > 1:
                _authors.append(_author)
                _space = 0
                _author = ''
        _sentry += 1
        _space += 1

    return _authors


def get_space_authors(file_data, first_author, institution):
    """
    获取全部作者
    情况2：以空格分隔的作者，作者姓名间不含空格
    """
    _authors = []
    _author = ''

    _authors_start = file_data.find(first_author)
    _authors_end = file_data.find(institution, _authors_start)
    _authors_str = file_data[_authors_start:_authors_end-1]

    _sentry = 0
    _space = 0
    while _sentry < len(_authors_str):
        if is_chinese(_authors_str[_sentry]):
            _author += _authors_str[_sentry]
            if _sentry == (len(_authors_str)-1):
                _authors.append(_author)
        elif len(_author) > 1:
            _authors.append(_author)
            _space = 0
            _author = ''
        _sentry += 1
        _space += 1

    return _authors


def authors_data(file_data, paper_name, institutions_data=[]):
    """
    get author data
    获取作者信息
    例如 基于word2vec的关键词提取算法_李跃鹏.txt
    根据_和.txt截取李跃鹏
    """
    _start = paper_name.rfind('_')
    _end = paper_name.find('.txt')
    paper_title = paper_name[:_start]
    first_author = paper_name[_start+1:_end]

    if not len(institutions_data):
        return {
            'authors': [],
            'first_author': first_author
        }

    institution = institutions_data[0]

    authors = get_comma_authors(
        file_data, paper_title, first_author, institution)

    if len(authors) == 1 and len(authors[0]) > 4:
        authors = get_space_authors(file_data, first_author, institution)

    authors = filter_authors(authors)

    return {
        'authors': authors,
        'first_author': first_author
    }


def journal_data(file_data, paper_name):
    """
    get journal data
    获取论文期刊信息,名称
    从最开始的中文到论文标题
    """
    EXCEPT_FIRST_WORDS = ['第', '卷', '期', '年', '月', '日']

    _start = paper_name.rfind('_')
    paper_title = paper_name[:_start]

    _file_data = format_paper(file_data)
    _journal_end = _file_data.find(paper_title)
    if _journal_end < 0:
        return ''
    _j_data = _file_data[:_journal_end]
    _count = -1
    journal_name = ''
    while 1:
        _count += 1
        if _count >= len(_j_data):
            break
        if len(journal_name) == 0 and (_j_data[_count] in EXCEPT_FIRST_WORDS):
            continue
        if is_chinese(_j_data[_count]):
            journal_name += _j_data[_count]
        elif len(journal_name):
            break

    return journal_name



def find_fund_project(format_data, mark_name):
    fund_name = mark_name
    funds_list = []
    maybe_words = ''
    besides_words = ['(', ')', '（', '）']

    _start = format_data.find(mark_name)
    _start -= 1

    if _start < 0:
        return funds_list

    # 向前补全
    while 1:
        if is_chinese(format_data[_start]):
            # print(format_data[_start])
            fund_name = format_data[_start]+maybe_words+fund_name
            # print(fund_name)
            maybe_words = ''
            _start -= 1
        else:
            if (format_data[_start] in besides_words) or format_data[_start].isalnum():
                maybe_words = format_data[_start]+maybe_words
                # 如果不是中文切不超过5个依旧插入，如A类，135计划,(...备注)
                if len(maybe_words) < 6:
                    _start -= 1
                    continue
            if len(fund_name):
                if fund_name != mark_name:
                    funds_list.append(fund_name)
                # 回到基金名称的最尾端
                _end = _start+len(fund_name)+len(maybe_words)
                if format_data.find(mark_name, _end) > -1:
                    fund_name = mark_name
                    maybe_words=''
                    _start = format_data.find(mark_name, _end) - 1
                    continue

            break

    return funds_list

def filter_funds(fund,fundlist):
    for _fund in fundlist:
        if _fund != fund and _fund.find(fund) > -1:
            return False
    return True

def fund_project(file_data):
    """
    获取文献基金项目
    """
    _file_data = format_paper(file_data)
    funds_list = []

    funds_list += find_fund_project(_file_data, '资助项目')
    funds_list += find_fund_project(_file_data, '启动项目')
    funds_list += find_fund_project(_file_data, '科研基金')
    funds_list += find_fund_project(_file_data, '科学基金')
    funds_list += find_fund_project(_file_data, '发展计划')
    funds_list += find_fund_project(_file_data, '计划项目')

    # 过滤相互包含的基金名称
    funds_list = list(filter(lambda _fund: filter_funds(_fund,funds_list) , funds_list))

    return funds_list
