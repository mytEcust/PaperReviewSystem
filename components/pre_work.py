# -*- coding: utf-8 -*-
"""
训练数据提取工作
"""

import os
import shutil
import json
import textract
from . import format_tool as ftool


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
        text = textract.process(paper_dir+paper)
        content = str(text, encoding="utf-8").strip()
        with open(txt_dir+paper.split(".")[0]+'.txt', 'w') as f:
            f.write(content)
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
            format_obj['author_institutions_data'] = institutions_data
            authors_data = ftool.authors_data(f_txt, paper, institutions_data)
            format_obj['first_author'] = authors_data['first_author']
            format_obj['authors'] = authors_data['authors']
            format_obj['journal_data'] = ftool.journal_data(f_txt, paper)
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
    author_instits = {}
    authors = {}
    fir_auth = {}
    journals = {}
    funds = {}
    ref_sources = {}
    for paper in os.listdir(format_dir):
        with open(format_dir+paper, 'r', encoding="utf-8") as txt:
            f_txt = txt.read()
            _f_json = json.loads(f_txt)

            _auth_instits = _f_json['author_institutions_data']
            _fir_auth = _f_json['first_author']
            _auths = _f_json['authors']
            _jou = _f_json['journal_data']
            _funds = _f_json['fund_project']
            _ref_sources = _f_json['references_source']

            # 作者所属机构
            for item in _auth_instits:
                if author_instits.get(item):
                    author_instits[item] += 1
                else:
                    author_instits[item] = 1

            # 作者
            for item in _auths:
                if authors.get(item):
                    authors[item] += 1
                else:
                    authors[item] = 1

            # 基金项目
            for item in _funds:
                if funds.get(item):
                    funds[item] += 1
                else:
                    funds[item] = 1

            # 参考文献的来源
            for item in _ref_sources:
                if ref_sources.get(item):
                    ref_sources[item] += 1
                else:
                    ref_sources[item] = 1

            # 发表期刊
            if journals.get(_jou):
                journals[_jou] += 1
            elif _jou:
                journals[_jou] = 1

            # 第一作者
            if fir_auth.get(_fir_auth):
                fir_auth[_fir_auth] += 1
            elif _fir_auth:
                fir_auth[_fir_auth] = 1

    with open(model_dir+'journals.json', 'w') as data:
        data.seek(0, 0)
        data.write(json.dumps(journals, ensure_ascii=False))

    with open(model_dir+'authors.json', 'w') as data:
        data.seek(0, 0)
        data.write(json.dumps(authors, ensure_ascii=False))

    with open(model_dir+'first-authors.json', 'w') as data:
        data.seek(0, 0)
        data.write(json.dumps(fir_auth, ensure_ascii=False))

    with open(model_dir+'author-institutions.json', 'w') as data:
        data.seek(0, 0)
        data.write(json.dumps(author_instits, ensure_ascii=False))

    with open(model_dir+'fund-projects.json', 'w') as data:
        data.seek(0, 0)
        data.write(json.dumps(funds, ensure_ascii=False))

    with open(model_dir+'ref-journals.json', 'w') as data:
        data.seek(0, 0)
        data.write(json.dumps(ref_sources, ensure_ascii=False))

    print("[END] format proportion")
