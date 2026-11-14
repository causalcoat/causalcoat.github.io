<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# coatlearn 使用文档

coatlearn 帮助你从非结构化数据中发现并测量有用因子，再分析因果结构与干预效应。因子是有明确含义和测量规则的属性，例如评论描述的甜度。现成 Python 接口读取文本列，论文框架还讨论图像与外部工具测量。

如果你有评分和评论，却还没有要分析的属性列，从[理解 COAT](<concepts.md>)开始。它解释为什么要发现变量，以及马尔可夫毯、因果图、调整集和效应估计分别有什么用。随后跟随[第一个分析](<quickstart.md>)，完成一次苹果评论的因子发现并读取结果。

## 学习

- [理解 COAT](<concepts.md>)：建立从非结构化资料到因果分析的概念联系。
- [安装与准备分析](<installation.md>)：从 PyPI 安装、下载示例并准备任务配置。
- [第一个分析](<quickstart.md>)：安装、查看配置、连接模型、运行并读取一个 MB 结果。

## 完成具体工作

- [准备数据](<data.md>)：选择输入列并编码自己的 CSV。
- [连接模型](<models.md>)：使用托管 Jev、聊天模型或 vLLM 服务。
- [部署本地 Kev](<kev.md>)：准备权重、启动服务并匹配客户端地址。
- [标注已有因子](<annotation.md>)：将固定定义转为测量表。
- [分析测量表与固定图](<causality.md>)：学习图、寻找调整集、估计效应，不调用语言模型。
- [通过代理使用](<agents.md>)：授权代理协助分析。

## 查阅接口与设置

- [发现接口](<discovery.md>)：MB、PAG、ADJ 的输入、调用与输出位置。
- [配置参考](<configuration.md>)：三份示例的完整设置和模型角色。
- [结果参考](<results.md>)：因子定义、图端点、调整集与估计字段。
- [包结构](<architecture.md>)：各功能模块的职责。

## 阅读方式

阅读[在线中文文档](https://causalcoat.github.io/docs/#/zh-cn/)或 [English](https://causalcoat.github.io/docs/#/)，可使用当前语言的全文搜索、代码复制和前后篇导航。已有源码时，也可以直接阅读 Markdown 或本地预览：

```bash
python3 -m http.server 8000
# 打开 http://localhost:8000/docs/#/zh-cn/
```

8000 是文档预览的示例端口，与模型服务端口无关。网页的 Docsify 和搜索资源随本站提供，不依赖 CDN 或托管搜索服务。
