<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# 配置参考

任务配置保存一次分析的数据选择、模型连接和统计设置。所附文件使用 TOML，一种用 `[task]` 等命名区段组织参数的文本格式。先用示例理解各项设置，再复制最接近自己问题的配置。

## 配置文件的组成

| 区段 | 保存什么 | 何时修改 |
| --- | --- | --- |
| `[task]` | 方法、数据路径、列名和明确的编码映射 | 换数据或研究问题时。 |
| `[models.<名称>]` | 连接类型、模型标识、地址、密钥变量与请求设置 | 换服务、模型或端口时。 |
| `[roles]` | 哪个命名模型负责哪项工作 | 分配提议、标注、审核与去重时。 |
| `[role_options.<角色>]` | 该角色的少量连接覆盖值 | 如单独限制审核并发时。 |
| `[analysis]` | 轮数、统计检验、显著性阈值、随机种子等 | 调整分析方案时。 |
| `[analysis.options]` | 因子格式、筛选与方法专属假设 | 明确需要某项分析政策时。 |

顶层 `schema_version = 1` 声明文件格式，直接保留即可，不是项目发布版本。`task.data` 的相对路径以配置文件所在目录为起点，而非终端工作目录。

## 三份示例的设置

| 项目 | [MB](<https://github.com/causalcoat/COAT-Learn/tree/main/config/mb.toml>) | [PAG](<https://github.com/causalcoat/COAT-Learn/tree/main/config/pag.toml>) | [ADJ](<https://github.com/causalcoat/COAT-Learn/tree/main/config/adj.toml>) |
| --- | --- | --- | --- |
| 行数 | 1000 | 1000，与 MB 共用 CSV | 2000 |
| 数值列 | `Score` | `Taste`、`Score` | `email_type`、`visit` |
| 文本列 | `Review` | `Review` | `post` |
| `rounds` | 5 | 2 | 2 |
| `test_method` | `fisherz` | `fisherz` | `mv_fisherz` |
| `alpha` | 0.001 | 0.001 | 0.001 |
| `concurrency` | 32 | 16 | 16 |
| `seed` | 0 | 42 | 42 |
| `fci_depth` | 2 | 2 | 2 |

三份配置都用 DeepSeek Flash 作为主模型，默认 Kev-9B 负责标注、审核与去重，并提供 Kev-4B 和 Jev 连接。因子采用 `general` 格式；定义格式修复开启；每条文本最多八个因子合并请求；共线性筛选的 VIF 阈值为 3；保存因子过程记录，不保存原始会话。

`alpha` 是条件独立性检验的显著性阈值，不是因果结论的可信度。`fisherz` 用偏相关检验条件独立性，依赖相应分布假设；`mv_fisherz` 是支持缺失值的变体。`fci_depth` 控制图搜索的条件变量深度。`rounds` 在各方法中的含义见[发现接口](<discovery.md>)。

## 模型角色

每个连接只在 `[models.<名称>]` 中定义一次，再由 `[roles]` 引用。名称是配置内的标签，真正发送给服务的模型标识保存在该连接的 `model` 字段。

```toml
[roles]
main = "main"
annotation = "kev9b"
judge = "kev9b"
dedup = "kev9b"
```

`main` 提出和修订因子，`annotation` 测量，`judge` 检查定义是否清楚并满足格式，`dedup` 比较是否为同一核心属性。后两项角色在所附配置中已开启，不因所有标注调用都自动存在。

可以将已开启的三个决策角色一起切换，不改变统计参数或主模型：

```bash
bash examples/pag.sh --decision-model kev4b
bash examples/pag.sh --decision-model jev
```

上述命令只显示配置；加 `--run` 才会执行。Kev 需要匹配的本地服务，见[部署说明](<kev.md>)。所附主模型以 `omit_temperature = true` 不发送温度参数；审核和去重并发分别限制为三，去重还提供了比较定义的任务背景。

## Python 参数

`RunConfig` 是公共分析参数的 Python 形式。直接调用不会自动读取 TOML，因此 Python 默认值与上面的示例设置可能不同。

| 字段 | Python 默认值 | 用途 |
| --- | --- | --- |
| `rounds` | 1 | 迭代次数或上限，含义依方法而定。 |
| `concurrency` | 16 | 标注工作线程数。 |
| `alpha` | 0.01 | 条件独立性检验的显著性阈值。 |
| `test_method` | `kci` | 传给 causal-learn 的检验方法。 |
| `seed` | 0 | NumPy 随机种子。 |
| `output_dir` | `None` | 过程输出位置；未指定时由方法选择并记录。 |
| `save_conversations` | `False` | 是否保存原始提示与响应。 |
| `options` | 空映射 | 方法专属设置。 |

常用 `options` 中，`factor_template="general"` 让因子定义声明量表、数值和提及条件。`vif_threshold` 用于移除与其他变量过于共线的候选；VIF 是方差膨胀因子，衡量一个变量被其他变量线性解释的程度。`annotation_batching` 控制同一文本的因子合并请求。

## ADJ 示例的筛选与估计

ADJ 示例要求候选在处理组和对照组中都具有足够的非缺失测量：各组提及率至少 0.05、至少 50 条。它还排除单因子五折预测处理或结果的准确率达到 0.9 的候选。这是该实验的明确筛选政策，不是“预测越好越没用”的一般结论。

每个调整集分别选择完整观测，要求保留比例至少 0.85。`cell_coverage_min=0.995` 要求可用行覆盖至少这一比例的声明取值组合；有序软分值按最近的声明档位计算组合。它描述组合覆盖，不是模型正确率，也不单独证明处理概率重叠。

成功估计的集合按变量数从多到少选择，同样大小时按处理概率范围从大到小选择，政策名为 `size_then_propensity_range`。图上最大的集合摘要与实际选中估计集合摘要分别保存，不保证变量最多就有最小估计误差。

## 研究假设

ADJ 示例声明 `assume_treatment_causes_outcome=true`，将处理到结果的方向作为已知前提；`assume_factors_precede_treatment=true` 声明因子先于处理。二者来自研究设定，不是本次从帖子发现的方向。

**调整可行性**（amenability）是广义调整准则对 PAG 的要求，用于排除可能因果路径首边上无法排除的潜在混杂。当前合成 ADJ 配置通过 `amenability_exempt=true` 显式豁免此要求，并在原因中记录数据生成前提。豁免后的结果依赖研究者假设，不能称为从原 PAG 通过了完整准则认证。

`break_cycles=true` 允许在最终图违反祖先图条件时考虑删边假设：枚举最少删边的方案，保护已知处理边，只估计各方案共同允许的调整集。原发现图保留，删边不是从数据中确认哪条边错误。库默认不启用此选项。

这些配置用于作者的具体合成研究。分析新数据时，先说明自己的前提，不要为了得到效应数值照搬豁免或删边政策。已提供假设、实际图处理和估计记录分别保存在[结果](<results.md>)中。

## 命令行覆盖

CLI 与 Python 读取相同任务。不加 `--run` 时，只显示本地配置和数据摘要：

```bash
coatlearn adj --config config/adj.toml
python3 -m coatlearn adj --config config/adj.toml
```

| 选项 | 作用 |
| --- | --- |
| `--config` | 选择任务配置。 |
| `--data` | 覆盖本次数据文件。 |
| `--decision-model` | 按配置内名称切换已开启的决策角色。 |
| `--output-dir` | 指定新输出目录。 |
| `--env-file` | 执行时读取指定的私有凭据文件。 |
| `--run` | 明确执行模型调用与分析。 |

各示例脚本是相应 CLI 命令的薄封装，可以接收同样的覆盖项。全部选项见 `python3 -m coatlearn adj --help`。
