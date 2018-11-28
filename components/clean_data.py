# -*- coding: utf-8 -*-
"""
数据清理与预处理
"""

import os
import json
from sklearn.neighbors import LocalOutlierFactor
import numpy as np


def trian_out_of_date(format_dir, model_dir):
    """
    聚类去除参考文献时间与文献发表时间差的时间的异常点
    参考文献
    http://scikit-learn.org/stable/auto_examples/neighbors/plot_lof.html#sphx-glr-auto-examples-neighbors-plot-lof-py
    https://zhuanlan.zhihu.com/p/37753692
    """
    print("[START] train out of date")
    origin_dates = []
    for paper in os.listdir(format_dir):
        with open(format_dir+paper, 'r', encoding="utf-8") as format_data:
            _format_data = format_data.read()
            _format_data = json.loads(_format_data)
            origin_dates += _format_data["out_of_date"]
    # 一维数据转二维
    origin_dates = list(zip(origin_dates, np.zeros_like(origin_dates)))
    clf = LocalOutlierFactor(n_neighbors=20)
    # fit非监督训练
    clf.fit(origin_dates)
    # 离群系数
    outlier = clf.kneighbors(origin_dates)[0].max(axis=1)
    # 参考文献发表日期 与 文献发表日期的时间差中 最后一个非离群点
    out_of_date = 0
    for i, _d in enumerate(origin_dates):
        if outlier[i] == 0 and _d[0] > out_of_date:
            out_of_date = _d[0]

    with open(model_dir+'outlier.txt', 'w') as data:
        data.write(str(out_of_date))
    print("[DONE] train out of date")


def clean_out_of_date(format_dir, model_dir):
    """
    清除时间差的异常点
    """
    print("[START] clean out of date")
    outlier = 0
    with open(model_dir+'outlier.txt', 'r') as data:
        outlier = data.read()
        outlier = int(outlier)

    for paper in os.listdir(format_dir):
        with open(format_dir+paper, 'r+', encoding="utf-8") as format_data:
            _format_data = format_data.read()
            _format_data = json.loads(_format_data)
            out_of_date = _format_data["out_of_date"]
            out_of_date = list(
                filter(lambda x: x <= outlier and x >= 0, out_of_date))
            _format_data["out_of_date"] = out_of_date
            # 将写入指针指向开头,即覆盖源文件
            format_data.seek(0, 0)
            format_data.truncate()
            format_data.write(json.dumps(_format_data, ensure_ascii=False))
    print("[DONE] clean out of date")
