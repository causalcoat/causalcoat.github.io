<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# 通过代理使用 COAT

可选 skill 帮助代理代表数据分析人员使用 COAT。它不同于 COAT 内部模型：面向使用者的代理选择并执行任务，内部提议器与标注器完成任务中的固定步骤。

通过你的代理应用提供的 skill 机制，安装或加载公开的 [coatlearn skill](<https://github.com/causalcoat/COAT-Learn/tree/main/skills/coatlearn/SKILL.md>)。它采用 `SKILL.md` 格式，不依赖特定厂商。安装时把 references 目录一起保留。

说明研究问题，并指定允许代理查看的数据。例如：“从这份 CSV 寻找与顾客评分有关的因子，调用模型前先展示配置。”

代理应先说明方法、数据列、模型角色、文本发送位置与计划输出目录，再取得模型执行授权。仅查看本地配置不会发请求。

执行后，代理应区分测量属性、统计关系、提供的因果假设与效应估计。它应依据保存结果解释本次运行，不在未经授权时改参数并继续调用模型。

不使用代理时，可以直接调用相同的 Python 接口与 CLI；分析不依赖任何代理平台。
