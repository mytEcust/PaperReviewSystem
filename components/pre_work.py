# -*- coding: utf-8 -*-
"""
训练数据提取工作
"""

import os
import shutil
import json
import textract
from . import format_tool as ftool

keys = ['words', 'paragraph', 'reference_counter', 'authors_pro', 'first_author_pro',
        'author_institutions_pro', 'journal_pro', 'fund_project_pro',
        'references_source_pro', 'out_of_date_pro',
        'most_similar', 'sims_pro']


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
        try:
            text = textract.process(paper_dir+paper)
            content = str(text, encoding="utf-8").strip()
            with open(txt_dir+paper.split(".")[0]+'.txt', 'w') as f:
                f.write(content)
        except Exception as e:
            print(e)
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
            publish_year = ftool.publish_data(f_txt)
            format_obj['publish_year'] = publish_year
            format_obj['out_of_date'] = ftool.out_of_date(
                publish_year, reference_obj['years'])
            institutions_data = ftool.author_institutions_data(f_txt)
            format_obj['author_institutions'] = institutions_data
            authors_data = ftool.authors_data(f_txt, paper, institutions_data)
            format_obj['first_author'] = authors_data['first_author']
            format_obj['authors'] = authors_data['authors']
            format_obj['journal'] = ftool.journal_data(f_txt, paper)
            format_obj['fund_project'] = ftool.fund_project(f_txt)
            format_obj['references_source'] = ftool.references_source(f_txt)
        with open(format_dir+paper.split(".")[0]+'.json', 'w') as f_format:
            f_format.write(json.dumps(format_obj, ensure_ascii=False))
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


def model_proportion(format_dir, model_dir):
    """
    将作者所属机构，作者，基金项目，参考文献的来源，发表期刊，第一作者
    生成出现次数数据
    """
    print("[START] format proportion")
    author_instits = {'list': {}}
    author_instits_count = 0
    authors = {'list': {}}
    authors_count = 0
    fir_auth = {'list': {}}
    fir_auth_count = 0
    journals = {'list': {}}
    journals_count = 0
    funds = {'list': {}}
    funds_count = 0
    ref_sources = {'list': {}}
    ref_sources_count = 0
    for paper in os.listdir(format_dir):
        with open(format_dir+paper, 'r+', encoding="utf-8") as txt:
            f_txt = txt.read()
            _f_json = json.loads(f_txt)

            _auth_instits = _f_json['author_institutions']
            _fir_auth = _f_json['first_author']
            _auths = _f_json['authors']
            _jou = _f_json['journal']
            _funds = _f_json['fund_project']
            _ref_sources = _f_json['references_source']

            # 作者所属机构
            for item in _auth_instits:
                author_instits_count += 1
                if author_instits['list'].get(item):
                    author_instits['list'][item] += 1
                else:
                    author_instits['list'][item] = 1

            # 作者
            for item in _auths:
                authors_count += 1
                if authors['list'].get(item):
                    authors['list'][item] += 1
                else:
                    authors['list'][item] = 1

            # 基金项目
            for item in _funds:
                funds_count += 1
                if funds['list'].get(item):
                    funds['list'][item] += 1
                else:
                    funds['list'][item] = 1

            # 参考文献的来源
            for item in _ref_sources:
                ref_sources_count += 1
                if ref_sources['list'].get(item):
                    ref_sources['list'][item] += 1
                else:
                    ref_sources['list'][item] = 1

            # 发表期刊
            if journals['list'].get(_jou):
                journals_count += 1
                journals['list'][_jou] += 1
            elif _jou:
                journals_count += 1
                journals['list'][_jou] = 1

            # 第一作者
            if fir_auth['list'].get(_fir_auth):
                fir_auth_count += 1
                fir_auth['list'][_fir_auth] += 1
            elif _fir_auth:
                fir_auth_count += 1
                fir_auth['list'][_fir_auth] = 1

    journals['total_num'] = journals_count
    authors['total_num'] = authors_count
    fir_auth['total_num'] = fir_auth_count
    author_instits['total_num'] = author_instits_count
    funds['total_num'] = funds_count
    ref_sources['total_num'] = ref_sources_count

    all_data = {
        'authors': authors,
        'first_author': fir_auth,
        'author_institutions': author_instits,
        'journal': journals,
        'fund_project': funds,
        'references_source': ref_sources
    }

    with open(model_dir+'sum-data.json', 'w') as data:
        data.write(json.dumps(all_data, ensure_ascii=False))
    print("[DONE] format proportion")


def average_data(format_dir, model_dir):
    """
    获取平均数据
    """
    print("[START] average data")
    _count = 0

    av_dict = {}

    for paper in os.listdir(format_dir):
        with open(format_dir+paper, 'r+', encoding="utf-8") as txt:
            f_txt = txt.read()
            _f_json = json.loads(f_txt)
            _count += 1
            for item in keys:
                if not av_dict.get(item):
                    av_dict[item] = 0
                av_dict[item] += _f_json[item]

    for item in keys:
        av_dict[item] = av_dict[item]/_count

    with open(model_dir+'average-data.json', 'w') as data:
        data.write(json.dumps(av_dict, ensure_ascii=False))

    print("[DONE] average data")


def proportion_data(format_dir, model_dir):
    """
    将文本数据量化为百分比
    """
    print("[START] proportion data")
    pro_dict = {}
    with open(model_dir+'sum-data.json', 'r') as data:
        pro_dict = data.read()
        pro_dict = json.loads(pro_dict)

    PRO_ELEMENT = [
        {'key_name': 'authors', 'pro_name': 'authors_pro'},
        {'key_name': 'first_author', 'pro_name': 'first_author_pro'},
        {'key_name': 'author_institutions', 'pro_name': 'author_institutions_pro'},
        {'key_name': 'journal', 'pro_name': 'journal_pro'},
        {'key_name': 'fund_project', 'pro_name': 'fund_project_pro'},
        {'key_name': 'references_source', 'pro_name': 'references_source_pro'}
    ]

    for paper in os.listdir(format_dir):
        with open(format_dir+paper, 'r+', encoding="utf-8") as txt:
            f_txt = txt.read()
            _f_json = json.loads(f_txt)

            for item in PRO_ELEMENT:
                _f_json = ftool.add_proportion(
                    pro_dict, _f_json, item['key_name'], item['pro_name'])

            # 平均发表时间差
            out_date = 0
            for _date in _f_json['out_of_date']:
                out_date += _date
            out_date = out_date/len(_f_json['out_of_date']) if out_date else 0
            _f_json['out_of_date_pro'] = round(out_date, 5)

            # 平均相似度
            _f_json['most_similar'] = _f_json['similar_paper'][0]['sim']

            sims_pro = 0
            for _sim in _f_json['similar_paper']:
                sims_pro += _sim['sim']
            sims_pro = sims_pro / \
                len(_f_json['similar_paper']) if sims_pro else 0
            _f_json['sims_pro'] = round(sims_pro, 16)

            txt.seek(0, 0)
            txt.truncate()
            txt.write(json.dumps(_f_json, ensure_ascii=False))
    print("[DONE] proportion data")


def svm_matrix(format_dir, model_dir, method='train'):
    """
    生成svm多维矩阵
    """
    print("[START] creat svm matrix")
    with open(model_dir+'average-data.json', 'r') as data:
        av_dict = data.read()
        av_dict = json.loads(av_dict)

    X = []
    paper_list = []
    for paper in os.listdir(format_dir):
        per_x = []
        with open(format_dir+paper, 'r', encoding="utf-8") as txt:
            f_txt = txt.read()
            _f_json = json.loads(f_txt)

            # 训练数据前最后的数据清理
            if _f_json['words'] < 1000 and method == 'train':
                continue

            for _key in keys:
                # 没有获取到值的取平均数据
                _value = _f_json[_key] if _f_json[_key] else av_dict[_key]
                per_x.append(_f_json[_key])

        X.append(per_x)
        paper_list.append(paper.split(".")[0])
        
    file_name = 'svm-matrix.json'
    if method != 'train':
        file_name = 'predict-svm-matrix.json'
        X = {
            'X': X,
            'paper_list': paper_list
        }

    with open(model_dir+file_name, 'w') as data:
        data.write(json.dumps(X, ensure_ascii=False))

    print("[DONE]] creat svm matrix")
