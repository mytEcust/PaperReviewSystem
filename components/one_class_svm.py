# -*- coding: utf-8 -*-
"""
单分类SVM
"""

import json
import numpy as np
from sklearn import svm
from sklearn.externals import joblib
from . import pre_work as pw

keys = pw.keys

# 由于OCSVM具有边界敏感的性质，故给予一定负阈值，
# 使得边界附近点不会被拒绝
# https://scikit-learn.org/stable/auto_examples/plot_anomaly_comparison.html#sphx-glr-auto-examples-plot-anomaly-comparison-py
THRESHOLD = -0.0001


def create_ocsvm_model(model_dir):
    """
    单分类SVM训练模型
    """
    X = []
    with open(model_dir+'svm-matrix.json', 'r', encoding="utf-8") as txt:
        f_txt = txt.read()
        X = json.loads(f_txt)
    X = np.array(X)
    # https://scikit-learn.org/stable/modules/generated/sklearn.svm.OneClassSVM.html
    clf = svm.OneClassSVM(nu=0.05, kernel="rbf", gamma=1/(len(keys)*X.std()))
    clf.fit(X)
    # 保存训练完的model
    joblib.dump(clf, model_dir+'clf-svm.pkl')


def run_ocsvm(model_dir):
    """
    运行单分类svm
    """
    # 读取Model
    clf = joblib.load(model_dir+'clf-svm.pkl')
    X = []
    with open(model_dir+'predict-svm-matrix.json', 'r', encoding="utf-8") as txt:
        f_txt = txt.read()
        data = json.loads(f_txt)
    paper_list = data['paper_list']
    X = np.array(data['X'])
    # X_train = clf.predict(X)
    X_detail = clf.decision_function(X)
    result_list = []
    for i, score in enumerate(X_detail):
        if score > THRESHOLD:
            result_list.append({
                "paper_name":paper_list[i],
                "score": score,
                "result":'通过'
            })
        else:
            result_list.append({
                "paper_name":paper_list[i],
                "score": score,
                "result":'失败'
            })
    
    return result_list
