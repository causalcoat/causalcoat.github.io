<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# 准备数据

发现接口需要每条观测的文本，以及你已经测得的目标变量。每行可以是一条评论及其评分，或一位顾客的帖子、是否收到邮件和是否访问网站。文字不必复述已有数值列；两者需要对应同一条观测。

## 按问题选择输入列

| 方法 | 已有数值列 | 非结构化内容 | 用途 |
| --- | --- | --- | --- |
| MB | 一个目标，如 `score` | 如 `text` | 寻找共同提供目标信息的因子。 |
| PAG | 一组初始变量，如 `taste`、`score` | 如 `text` | 发现更多因子，细化初始变量的结构信息。 |
| ADJ | 处理与结果，如 `sent`、`visited` | 如 `post` | 寻找调整变量并估计指定效应。 |

本包现成接口使用字符串文本列，不直接读取图片或外部数据库。已有数值分析列应为有限数值且不缺失，文本列应为非空字符串。后续从文本标注的因子可以因未提及而缺失。

只有指定的列进入发现，其他列可以留在 CSV 中。特别是合成数据中记录的真实因子值，不会因为存在于文件中就自动用于分析。程序保留原行序和重复文本。

## 了解两份示例

[苹果 graph1 CSV](<https://github.com/causalcoat/COAT-Learn/tree/main/data/apple_reviews_PAG_graph1.csv>)有 1000 行，来自作者的合成苹果评论研究数据。MB 读取 `Score`、`Review`；PAG 读取 `Taste`、`Score`、`Review`。两种方法共享数据，但问题不同：前者寻找目标信息集合，后者利用补充变量细化结构。这不是收集自电商平台的真实顾客评论。

[Hillstrom 帖子 CSV](<https://github.com/causalcoat/COAT-Learn/tree/main/data/hillstrom_email_visit_post.csv>)有 2000 行，包含合成顾客帖子及邮件、访问记录。它采用研究中的混杂设置，不是原始随机化 Hillstrom 顾客表。ADJ 只读取 `email_type`、`visit`、`post`，不直接读取隐藏的顾客属性。

Hillstrom 文件用 `email_type` 的 `Yes` 表示发送，空单元格表示未发送；`visit` 用 `Yes/No` 表示访问与未访问。[ADJ 配置](<https://github.com/causalcoat/COAT-Learn/tree/main/config/adj.toml>)显式将它们转换为 1/0。这里“空单元格等于对照组”是这份数据的特定约定，不是通用缺失值处理规则。来源记录与文件哈希见[数据清单](<https://github.com/causalcoat/COAT-Learn/tree/main/data/README.md>)。

## 使用自己的表

输入可以是带表头的本地 CSV，或 pandas DataFrame。先明确观测单位与各列含义，再指定要读取的列。若处理和结果还不是数值，在调用前明确编码：

```python
import pandas as pd

frame = pd.read_csv("customers.csv")
frame["sent"] = frame["email_label"].map({"sent": 1, "not_sent": 0})
frame["visited"] = frame["visit_label"].map({"yes": 1, "no": 0})
print(frame[["sent", "visited"]].value_counts())
```

`sent=1` 定义要研究的处理，`sent=0` 定义对照。结果的观测时间应与问题相符，例如发送之后的访问记录。将准备好的 `frame` 传给[发现接口](<discovery.md>)即可。TOML 用户可复制相近任务配置，修改 `[task]` 中的数据路径和列名；路径相对于配置文件。

不要直接把当前 ADJ 示例的方向先验和调整豁免复制到新数据。它们依赖示例的生成方式，说明见[研究假设](<configuration.md#研究假设>)。

## 确认文本发送位置

托管模型在请求中接收文本。主模型收到选中的提议示例，标注模型收到逐条待赋值文本，审核记录可能包含提出因子时的示例。本地 Kev 只将决策请求留在本机，托管主模型仍会接收提议示例。

输出目录也可能含原始内容。因子过程记录可以保存示例与回答，开启会话保存后还会保留原始提示与响应。因此应按源数据的敏感程度保存整个输出目录，不把密钥放进数据、配置或结果。

两份示例 CSV 采用 [CC BY 4.0](<https://github.com/causalcoat/COAT-Learn/tree/main/data/LICENSE>)，与软件的 [Apache-2.0 许可](<https://github.com/causalcoat/COAT-Learn/tree/main/LICENSE>)分开。再分发时保留[来源与署名信息](<https://github.com/causalcoat/COAT-Learn/tree/main/data/README.md>)，并说明所作修改。
