# -*- coding: utf-8 -*-
"""
入口函数
"""

__author__ = 'myt'

from configobj import ConfigObj

from components import pre_work as pw
from components import doc2vec as dv
from components import clean_data as cd
from components import one_class_svm as svm
from components import report as rp

config = ConfigObj('../config/default.conf')

PAPER_DIR = config['train']['paper_dir']
TEST_DIR = config['train']['test_dir']
TXT_DIR = config['train']['txt_dir']
TRAIN_DIR = config['train']['train_dir']
FORMAT_DIR = config['train']['format_dir']
MODEL_DIR = config['train']['model_dir']

EXEC_DIR = config['predict']['paper_dir']
EXEC_TXT_DIR = config['predict']['txt_dir']
EXEC_FORMAT_DIR = config['predict']['format_dir']
EXEC_TRAIN_DIR = config['predict']['train_dir']
EXEC_REPORT_DIR = config['predict']['report_dir']


def creat_model():
    """
    段落向量及OCSVM的建模
    """
    print('--- START CREATE MODEL ---')
    # 初始化工作
    pw.init_dir([TXT_DIR, TRAIN_DIR, FORMAT_DIR, MODEL_DIR])
    pw.switch_pdf(PAPER_DIR, TXT_DIR)
    pw.format_paper(TXT_DIR, FORMAT_DIR)
    pw.format_train_data(TXT_DIR, TRAIN_DIR)

    # 段落向量计算相似度
    dv.train_datasest(TRAIN_DIR, MODEL_DIR)
    dv.run_model(TRAIN_DIR, FORMAT_DIR, MODEL_DIR)

    # 数据预处理
    cd.trian_out_of_date(FORMAT_DIR, MODEL_DIR)
    cd.clean_out_of_date(FORMAT_DIR, MODEL_DIR)
    pw.model_proportion(FORMAT_DIR, MODEL_DIR)
    pw.proportion_data(FORMAT_DIR, MODEL_DIR)
    pw.average_data(FORMAT_DIR, MODEL_DIR)

    # 单分类svm
    pw.svm_matrix(FORMAT_DIR, MODEL_DIR, 'train')
    svm.create_ocsvm_model(MODEL_DIR)
    print('--- DONE CREATE MODEL ---')


def predict_model():
    """
    预测数据
    """
    print('--- START PREDICT MODEL ---')
    # 1. clean model data
    pw.init_dir([EXEC_TXT_DIR, EXEC_FORMAT_DIR,
                 EXEC_TRAIN_DIR, EXEC_REPORT_DIR])
    # 2. pdf2txt
    pw.switch_pdf(EXEC_DIR, EXEC_TXT_DIR)
    # 3. get basic feature
    pw.format_paper(EXEC_TXT_DIR, EXEC_FORMAT_DIR)
    # 4. format txt to train's data for doc2dev
    pw.format_train_data(EXEC_TXT_DIR, EXEC_TRAIN_DIR)
    # 5. doc2dev
    dv.run_model(EXEC_TRAIN_DIR, EXEC_FORMAT_DIR, MODEL_DIR)
    # 6. clean out of data
    cd.clean_out_of_date(EXEC_FORMAT_DIR, MODEL_DIR)
    # 7. format data to proportion data
    pw.proportion_data(EXEC_FORMAT_DIR, MODEL_DIR)
    # 8. create svm matrix
    pw.svm_matrix(EXEC_FORMAT_DIR, MODEL_DIR, 'predict')
    # 9. run ocsvm
    data_list = svm.run_ocsvm(MODEL_DIR)
    # 10. make report
    rp.generate_report(data_list, EXEC_FORMAT_DIR, MODEL_DIR, EXEC_REPORT_DIR)
    print('--- DONE PREDICT MODEL ---')


if __name__ == '__main__':
    creat_model()
    predict_model()
