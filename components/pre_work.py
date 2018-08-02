# -*- coding: utf-8 -*-
"""
训练数据提取工作
"""

import os
import shutil
import json
import textract
from . import format_tool as ftool


def init_dir(dirs):
    """
    初始化文件夹
    """
    for _dir in dirs:
        if os.path.isdir(_dir):
            shutil.rmtree(_dir)
        os.makedirs(_dir)


def switch_pdf(paper_dir, txt_dir):
    """
    将pdf读取为txt
    """
    print("[START] switch paper to txt")
    for paper in os.listdir(paper_dir):
        text = textract.process(paper_dir+paper)
        content = str(text, encoding="utf-8").strip()
        with open(txt_dir+paper.split(".")[0]+'.txt', 'w') as f:
            f.write(content)
    print("[DONE] switch paper to txt")


def format_paper(txt_dir, format_dir):
    """
    获取论文基本特征
    """
    print("[START] format paper")
    for paper in os.listdir(txt_dir):
        with open(txt_dir+paper, 'r', encoding="utf-8") as txt:
            f_txt = txt.read()
            format_obj = {}
            format_obj['words'] = ftool.word_counter(f_txt)
            format_obj['paragraph'] = ftool.paragraph_counter(f_txt)
            reference_obj = ftool.reference_counter(f_txt)
            format_obj['reference_counter'] = reference_obj['counter']
            format_obj['reference_years'] = reference_obj['years']
            publish_year = ftool.publish_date(f_txt)
            format_obj['publish_year'] = publish_year
            format_obj['out_of_date'] = ftool.out_of_date(
                publish_year, reference_obj['years'])
        with open(format_dir+paper.split(".")[0]+'.json', 'w') as f_format:
            f_format.write(json.dumps(format_obj))
    print("[DONE] format paper")


def format_train_data(txt_dir, train_dir):
    """
    格式化训练数据
    """
    print("[START] format train data")
    for paper in os.listdir(txt_dir):
        with open(txt_dir+paper, 'r', encoding="utf-8") as txt:
            f_txt = txt.read()
            content_list = list(f_txt)
            i = 0
            while i < len(content_list):
                if not ftool.is_chinese(content_list[i]):
                    content_list[i] = ''
                i += 1
            content = ''.join(content_list)
        with open(train_dir+paper.split(".")[0]+'.txt', 'w') as f_train:
            f_train.write(content)
    print("[DONE] format train data")
