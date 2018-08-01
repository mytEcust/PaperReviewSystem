# -*- coding: utf-8 -*-
"""
入口函数
"""

__author__ = 'myt'

import os
import numpy as np
from components import pre_work as pw
from gensim.test.utils import common_texts
from gensim.test.utils import get_tmpfile
from gensim.models.doc2vec import Doc2Vec, TaggedDocument

PAPER_DIR = './paper_data/'
TXT_DIR = './txt_data/'
TRAIN_DIR = './train_data/'
FORMAT_DIR = './format_data/'

pw.init_dir([TXT_DIR, TRAIN_DIR, FORMAT_DIR])
pw.switch_pdf(PAPER_DIR, TXT_DIR)
pw.format_paper(TXT_DIR, FORMAT_DIR)
pw.format_train_data(TXT_DIR, TRAIN_DIR)

# https://blog.csdn.net/juanjuan1314/article/details/75124046/


def get_datasest():
    docs = []
    for paper in os.listdir(TRAIN_DIR):
        with open(TRAIN_DIR+paper, 'r', encoding="utf-8") as train_data:
            _train_data = train_data.read()
            docs.append(_train_data)
    x_train = []
    for i, text in enumerate(docs):
        word_list = text.split(' ')
        w_len = len(word_list)
        word_list[w_len-1] = word_list[w_len-1].strip()
        document = TaggedDocument(word_list, tags=[i])
        x_train.append(document)

    return x_train


def getVecs(model, corpus, size):
    vecs = [np.array(model.docvecs[z.tags[0]].reshape(1, size))
            for z in corpus]
    return np.concatenate(vecs)


def train(x_train, size=200, epoch_num=1):
    model_dm = Doc2Vec(x_train, min_count=1, window=3,
                       size=size, sample=1e-3, negative=5, workers=4)
    model_dm.train(x_train, total_examples=model_dm.corpus_count, epochs=70)
    model_dm.save('./model')

    return model_dm


def test():
    model_dm = Doc2Vec.load("./model")
    test_text = []
    with open(TRAIN_DIR+'对主成分分析法三个问题的剖析_许淑娜.txt', 'r', encoding="utf-8") as td:
        _td = td.read()
        test_text.append(_td)
    inferred_vector_dm = model_dm.infer_vector(test_text)
    print(inferred_vector_dm)
    sims = model_dm.docvecs.most_similar([inferred_vector_dm], topn=10)
    print(sims)
    return sims


print("[START] doc2vec")
_x_train = get_datasest()
model_dm = train(_x_train)
sims = test()
for count, sim in sims:
    sentence = _x_train[count]
    words = ''
    for word in sentence[0]:
        words = words + word + ' '
        print(sim)
print("[DONE] doc2vec")
