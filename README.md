# Paper-Review-System

## Environment requirements
- Python >=3.4

## Run

Install dependencies

```
pip install -r requirement.txt
```

### For Dev
```
python3 index.py
```

### 文件夹说明
* components文件夹中维护了所有的分析模块
* 参考文献及参考文献标注中为写代码时阅读的文献资料
* paper_data中为最原始的从知网上下载的文献pdf
* txt_data中为将pdf解析为txt后的结果文献
* train_data中是经过处理的文献资料用于词向量的训练集
* model文件夹中是训练完成的模型数据
* format_data中存放的是最后分析得出的文献数据


### 模块说明

具体的函数作用在代码中都有详尽的注释

* pre_work.py为预处理模块
* format_tool.py为格式化工具模块
* doc2vec.py为词向量训练模块

### 流程说明
1. 初始化文件夹
2. 将pdf文献读取为txt
3. 获取论文基本特征,包括字数,段落数,参考文献数,参考文献发表年限,论文发表年限,论文与参考文献发表年限的差
4. 预处理文献预料
5. 训练语料的词向量模型
6. 获取与文献最相似的文献极其相似程度

### TODO (按优先级排列)
1. 预处理文献特征数据,去除异常点
2. 进行单分类SVM的训练
3. 完整的文献评审流程
4. 参考年限的获取还无法完全准确获取,有待完善
5. 特征添加

```diff
- 作者信息
- 作者单位
+ 发表期刊的名称
+ 作者简介
+ 基金项目
+ 参考文献的来源
+ 参考文献的来源的权威
+ 网上的来源的影响因子
```