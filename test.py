# -*- coding: utf-8 -*-
"""
测试函数
"""

from configobj import ConfigObj

from components import pre_work as pw
from components import doc2vec as dv
from components import clean_data as cd
from components import one_class_svm as svm
from components import report as rp

config = ConfigObj('./config/default.conf')

PAPER_DIR = config['ecice']['paper_dir']
TXT_DIR = config['ecice']['txt_dir']
TRAIN_DIR = config['ecice']['train_dir']
FORMAT_DIR = config['ecice']['format_dir']
MODEL_DIR = config['ecice']['model_dir']

JOS = {}
JOS['EXEC_DIR'] = config['jos']['paper_dir']
JOS['EXEC_TXT_DIR'] = config['jos']['txt_dir']
JOS['EXEC_FORMAT_DIR'] = config['jos']['format_dir']
JOS['EXEC_TRAIN_DIR'] = config['jos']['train_dir']
JOS['EXEC_REPORT_DIR'] = config['jos']['report_dir']

CEAJ = {}
CEAJ['EXEC_DIR'] = config['ceaj']['paper_dir']
CEAJ['EXEC_TXT_DIR'] = config['ceaj']['txt_dir']
CEAJ['EXEC_FORMAT_DIR'] = config['ceaj']['format_dir']
CEAJ['EXEC_TRAIN_DIR'] = config['ceaj']['train_dir']
CEAJ['EXEC_REPORT_DIR'] = config['ceaj']['report_dir']


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


def predict_model(predict_data):
    """
    预测数据
    """
    print('--- START PREDICT MODEL ---')
    EXEC_DIR = predict_data['EXEC_DIR']
    EXEC_TXT_DIR = predict_data['EXEC_TXT_DIR']
    EXEC_FORMAT_DIR = predict_data['EXEC_FORMAT_DIR']
    EXEC_TRAIN_DIR = predict_data['EXEC_TRAIN_DIR']
    EXEC_REPORT_DIR = predict_data['EXEC_REPORT_DIR']

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
    predict_model(JOS)
    predict_model(CEAJ)
