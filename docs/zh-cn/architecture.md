<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# 包结构

包按功能划分。每个模块都有独立用途，发现流程组合其他模块，不包揽所有操作。

| 模块 | 职责 |
| --- | --- |
| `models` | OpenAI-compatible 聊天与原生 System One HTTP 调用 |
| `annotation` | 定义解析、测量、审核与概念比较 |
| `discovery` | MB、PAG、ADJ 迭代 |
| `causality` | 条件独立性、图操作、调整与 IPW |
| `cli` | 解析参数，调用共用配置与执行逻辑 |
| `utils` | 通用日志和显式采样辅助 |

包根保留五个方便入口：`ModelConfig`、`RunConfig`、`run_mb`、`run_pag`、`run_adj`。独立标注和因果操作从对应模块导入。

模型传输不解释因子数值，数值映射由标注维护。因果计算读取测量值与图假设，不调用模型。因此各阶段也能在完整发现流程之外使用。

读取配置只生成任务描述，不创建模型客户端。本地检查选择指定列，记录明确的编码映射。执行时调用与 Python 使用者相同的根函数，再保存结果。

[源码来源](<https://github.com/causalcoat/COAT-Learn/tree/main/SOURCE_MAP.md>)记录研究实现的来源。安装与使用本项目不需要历史运行记录。
