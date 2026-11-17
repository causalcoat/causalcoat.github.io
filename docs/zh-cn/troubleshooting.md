<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# 本地依赖

所附 TOML 示例选择决策模型比较因子概念，不需要 WordNet 完成这一步。直接 Python 发现调用若未配置该比较器，会使用基于名称重合的路径，需要已安装的 WordNet 语料。

在运行分析的 Python 环境中显式安装语料：

```bash
python3 -m nltk.downloader wordnet omw-1.4
```

本包不会在分析时自动下载语料。

模型地址与凭据见[连接模型](<models.md>)，匹配的本地决策服务见[部署 Kev](<kev.md>)。命令行选项可通过 `python3 -m coatlearn mb --help` 查看。
