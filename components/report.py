# -*- coding: utf-8 -*-
"""
生成报告
"""
import json


def _report_words(words, av_dict, report):
    avg_words = int(av_dict["words"])
    _report = "字数："+str(words)+"；平均字数："+str(avg_words)+"\n"
    report += _report
    return report


def _report_para(paragraph, av_dict, report):
    avg_para = int(av_dict["paragraph"])
    _report = "段落数："+str(paragraph)+"；平均段落数："+str(avg_para)+"\n"
    report += _report
    return report


def _report_refs(reference_counter, av_dict, report):
    avg_ref = int(av_dict["reference_counter"])
    _report = "参考文献数："+str(reference_counter)+"；平均参考文献数："+str(avg_ref)+"\n"
    report += _report
    return report


def _report_ref_date(out_of_date_pro, av_dict, report):
    avg_ref = round(av_dict["out_of_date_pro"], 2)
    out_of_date_pro = round(out_of_date_pro, 2)
    _report = "参考文献发表时间与该文献发表时间差：" + \
        str(out_of_date_pro)+"；平均值："+str(avg_ref)+"\n"
    report += _report
    return report


def _report_ref_sou(references_source_pro, av_dict, report):
    if references_source_pro:
        avg_ref_sou = round(av_dict["references_source_pro"], 2)
        references_source_pro = round(references_source_pro, 2)
        _report = "参考文献的来源权威占比（百分之）：" + \
            str(avg_ref_sou)+"；平均值："+str(references_source_pro)+"\n"
        report += _report
    else:
        _report = "无法获取参考文献的来源\n"
        report += _report
        report
    return report


def _report_sim(similar_paper, av_dict, report):
    avg_sim_pro = round(av_dict["sims_pro"], 3)
    avg_sim_most = round(av_dict["most_similar"], 3)
    most_sims = round(similar_paper[0]["sim"], 3)
    most_sim_paper = similar_paper[0]["name"]
    sum_sim = 0
    for _paper in similar_paper:
        sum_sim += _paper["sim"]
    avg_sum = round(sum_sim/len(similar_paper), 3)

    _report = "最相似文献："+str(most_sim_paper)+"；相似度：" + \
        str(most_sims)+"；平均最大相似度："+str(avg_sim_most)+"\n" + \
        "最相似的十篇文献的平均相似度："+str(avg_sum)+"；平均值："+str(avg_sim_pro)+"\n"
    report += _report
    return report


def _report_jou(journal_pro, av_dict, report):
    if journal_pro:
        avg_Jou = round(av_dict["journal_pro"], 2)
        journal_pro = round(journal_pro, 2)
        _report = "发表期刊权威占比（百分之）："+str(avg_Jou)+"；平均值："+str(journal_pro)+"\n"
        report += _report
    else:
        _report = "无法获取发表期刊\n"
        report += _report
        report
    return report


def _report_fund(fund_project_pro, av_dict, report):
    if fund_project_pro:
        avg_Fund = round(av_dict["fund_project_pro"], 2)
        fund_project_pro = round(fund_project_pro, 2)
        _report = "基金项目权威占比（百分之）：" + \
            str(fund_project_pro)+"；平均值："+str(avg_Fund)+"\n"
        report += _report
    else:
        _report = "无法获取基金项目\n"
        report += _report
        report
    return report


_map_report = {
    "words": _report_words,
    "paragraph": _report_para,
    "reference_counter": _report_refs,
    "out_of_date_pro": _report_ref_date,
    "references_source_pro": _report_ref_sou,
    "similar_paper": _report_sim,
    "journal_pro": _report_jou,
    "fund_project_pro": _report_fund
}


def _get_avg_data(model_dir):
    with open(model_dir+"average-data.json", 'r', encoding="utf-8") as avg_data:
        av_dict = avg_data.read()
        av_dict = json.loads(av_dict)
        return av_dict


def generate_report(data_list, format_dir, model_dir, report_dir):
    print("[START] generate report")
    av_dict = _get_avg_data(model_dir)
    for _data in data_list:
        report = ""
        with open(format_dir+_data["paper_name"].split(".")[0]+'.json', 'r', encoding="utf-8") as format_data:
            format_data = format_data.read()
            format_data = json.loads(format_data)
            _report = "评审建议："+str(_data['result']) + \
                "；评审系数："+str(_data['score'][0])+"\n"
            report += _report
            for _key in format_data.keys():
                if _key in _map_report:  
                    report = _map_report[_key](
                        format_data[_key], av_dict, report)
        with open(report_dir+_data["paper_name"].split(".")[0]+'.txt', 'w', encoding="utf-8") as r_data:
            r_data.write(report)
    print("[DONE] agenerate report")
