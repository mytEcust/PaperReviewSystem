# -*- coding: utf-8 -*-
"""
数据清理与预处理
"""

import os
import json
from sklearn.neighbors import LocalOutlierFactor
import numpy as np


def clean_out_of_date(format_dir):
    """
    聚类去除参考文献时间与文献发表时间差的时间的异常点
    """
    dates = []
    origin_dates = []
    show_datas = []
    for paper in os.listdir(format_dir):
        with open(format_dir+paper, 'r', encoding="utf-8") as format_data:
            _format_data = format_data.read()
            _format_data = json.loads(_format_data)
            origin_dates += _format_data["out_of_date"]
            for date in _format_data["out_of_date"]:
                dates.append([date, 0])
    origin_dates = list(zip(origin_dates, np.zeros_like(origin_dates)))
    clf = LocalOutlierFactor(n_neighbors=20)
    # fit非监督训练
    clf.fit(origin_dates)
    # scores_pred = clf.negative_outlier_factor_
    # for i, _d in enumerate(origin_dates):
    #     show_datas.append([_d, y_pred[i]])
    a = clf.kneighbors(origin_dates)[0].max(axis=1)
    print('离群系数')
    print(a)

    # http://scikit-learn.org/stable/auto_examples/neighbors/plot_lof.html#sphx-glr-auto-examples-neighbors-plot-lof-py
    # np.random.seed(42)

    # # Generate train data
    # X = 0.3 * np.random.randn(100, 2)
    # # Generate some abnormal novel observations
    # X_outliers = np.random.uniform(low=-4, high=4, size=(20, 2))
    # print(X)
    # print('-------------')
    # print(X_outliers)
    # X = np.r_[X + 2, X - 2, X_outliers]

    # # X=dates

    # # fit the model
    # clf = LocalOutlierFactor(n_neighbors=20)
    # y_pred = clf.fit_predict(X)
    # y_pred_outliers = y_pred[200:]
    # # plot the level sets of the decision function
    # xx, yy = np.meshgrid(np.linspace(-5, 5, 50), np.linspace(-5, 5, 50))
    # Z = clf._decision_function(np.c_[xx.ravel(), yy.ravel()])
    # Z = Z.reshape(xx.shape)

    # plt.title("Local Outlier Factor (LOF)")
    # plt.contourf(xx, yy, Z, cmap=plt.cm.Blues_r)

    # a = plt.scatter(X[:200, 0], X[:200, 1], c='white',
    #                 edgecolor='k', s=20)
    # b = plt.scatter(X[200:, 0], X[200:, 1], c='red',
    #                 edgecolor='k', s=20)
    # plt.axis('tight')
    # plt.xlim((-5, 5))
    # plt.ylim((-5, 5))
    # plt.legend([a, b],
    #         ["normal observations",
    #             "abnormal observations"],
    #         loc="upper left")
    # plt.show()
