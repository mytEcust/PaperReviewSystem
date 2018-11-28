# -*- coding: utf-8 -*-
"""
段落向量训练模型
"""

import os
import json
import jieba
from gensim.models.doc2vec import Doc2Vec, TaggedDocument


def train_datasest(train_dir, model_dir):
    """
    训练语料预处理至TaggedDocument
    """
    print("[START] train doc2vec")
    papers = []
    for paper in os.listdir(train_dir):
        with open(train_dir+paper, 'r', encoding="utf-8") as train_data:
            train_data = train_data.read()
            papers.append({
                'train_data': train_data,
                'name': paper.strip(".txt")
            })
    # 用于存放语料
    paper_train = []
    # 由编号映射博客ID的字典
    paper_dict = {}
    for i, paper in enumerate(papers):
        word_list = list(jieba.cut(paper['train_data']))
        paper_dict[i] = paper['name']
        document = TaggedDocument(word_list, tags=[i])
        paper_train.append(document)

    # 保存文献字典
    with open(model_dir+'paper-dict.json', 'w') as f_json:
        # json字符化时不让中文转换为unicode
        f_json.write(json.dumps(paper_dict, ensure_ascii=False))

    # 模型的初始化，设置参数
    # min_cout 忽略总频率低于这个的所有单词
    # window 预测的词与上下文词之间最大的距离, 用于预测
    # vector_size 特征向量的维数
    # negative 接受杂质的个数
    # worker 工作模块数
    model_dm = Doc2Vec(paper_train, min_count=1, window=3,
                       vector_size=200, sample=1e-3, negative=5, workers=4)
    # corpus_count是文件个数
    # epochs 训练次数
    model_dm.train(
        paper_train, total_examples=model_dm.corpus_count, epochs=70)
    model_dm.save(model_dir+'doc2vec-model')
    print("[DONE] train doc2vec")


def load_paper_index(model_dir):
    """
    读取文献字典
    """
    with open(model_dir+'paper-dict.json', 'r', encoding="utf-8") as f_json:
        paper_dict = f_json.read()
        paper_dict = json.loads(paper_dict)
        return paper_dict


def set_similar_paper(paper_similar, format_dir):
    """
    保存文献最相似的文献及相似程度
    """
    for paper in os.listdir(format_dir):
        p_name = paper.split('.json')[0]
        with open(format_dir+paper, 'r+', encoding="utf-8") as p_json:
            _p_json = p_json.read()
            _p_json = json.loads(_p_json)
            _p_json['similar_paper'] = paper_similar[p_name]
            # 将写入指针指向开头,即覆盖源文件
            p_json.seek(0, 0)
            p_json.truncate()
            p_json.write(json.dumps(_p_json, ensure_ascii=False))


def run_model(train_dir, format_dir, model_dir):
    """
    检测论文相似度
    """
    print("[START] run_model")
    # 加载训练的模型
    model_dm = Doc2Vec.load(model_dir+'doc2vec-model')
    # 加载文献字典
    paper_dict = load_paper_index(model_dir)
    paper_similar = {}
    for paper in os.listdir(train_dir):
        with open(train_dir+paper, 'r', encoding="utf-8") as test_d:
            test_d = test_d.read()
            test_text = list(jieba.cut(test_d))
            inferred_vector_dm = model_dm.infer_vector(test_text)
            # topn 降序显示相似度最大的15个taggeddocument
            sims = model_dm.docvecs.most_similar([inferred_vector_dm], topn=15)
            paper_name = paper.split('.txt')[0]
            paper_similar[paper_name] = []
            i = 0
            for index, sim in sims:
                # 是自己则跳过
                if paper_dict[str(index)] == paper_name:
                    continue
                paper_name = paper.split('.txt')[0]
                paper_similar[paper_name].append({
                    'name': paper_dict[str(index)],
                    'sim': sim*100  # 百分制
                })
                # 获取10篇后结束
                if len(paper_similar[paper_name]) == 10:
                    break

    set_similar_paper(paper_similar, format_dir)
    print("[DONE] run_model")
