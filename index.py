# -*- coding: utf-8 -*-
"""
入口函数
"""

__author__ = 'myt'

from components import pre_work as pw
from components import doc2vec as dv


PAPER_DIR = './paper_data/'
TEST_DIR = './test_data/'
TXT_DIR = './txt_data/'
TRAIN_DIR = './train_data/'
FORMAT_DIR = './format_data/'
MODEL_DIR = './model/'

if __name__ == '__main__':
    # 初始化工作
    pw.init_dir([TXT_DIR, TRAIN_DIR, FORMAT_DIR, MODEL_DIR])
    pw.switch_pdf(PAPER_DIR, TXT_DIR)
    pw.format_paper(TXT_DIR, FORMAT_DIR)
    pw.format_train_data(TXT_DIR, TRAIN_DIR)

    # 段落向量计算相似度
    dv.train_datasest(TRAIN_DIR)
    dv.run_model(TRAIN_DIR, FORMAT_DIR)
