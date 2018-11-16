# -*- coding: utf-8 -*-
"""
单分类SVM
"""

import numpy as np
from sklearn import svm
import json

keys = ['words', 'paragraph', 'reference_counter', 'authors_pro', 'first_author_pro',
        'author_institutions_pro', 'journal_pro', 'fund_project_pro',
        'references_source_pro', 'out_of_date_pro',
        'most_similar', 'sims_pro']


def one_class_svm(model_dir):
    X = []
    with open(model_dir+'svm-matrix.json', 'r', encoding="utf-8") as txt:
        f_txt = txt.read()
        X = json.loads(f_txt)
    X = np.array(X)
    # https://scikit-learn.org/stable/modules/generated/sklearn.svm.OneClassSVM.html
    clf = svm.OneClassSVM(nu=0.05, kernel="rbf", gamma=1/(len(keys)*X.std()))
    clf.fit(X)
    X_train = clf.predict(X)
    X_detail = clf.decision_function(X)

    count = 0
    for item in X_detail:
        if item*-10000 > 1:
            print(item*-10000)
            count += 1
    print(count)
