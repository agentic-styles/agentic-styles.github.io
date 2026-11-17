# Agentic Architecture Lab

面向工程师与架构师的质量属性驱动设计课程。通过合成的 Booking Precheck 场景，学习从业务证据、基线与架构压力出发，选择职责、控制权和协作契约，再用实验作出 Adopt、Adapt 或 Reject 决策。

## 本模块包含什么

- 71 页课程 Slides、可选择的 Optional Detail 与讲师备注。
- 两个可直接讨论的合成案例，以及设计练习和验收门槛。
- 从质量场景、设计手段、Pattern 到接口与 ADR 的推理路径。
- 对统一评测接口、Dataset、Trace 和指标的设计讲解。

## 当前运行边界

当前仓库负责构建和浏览课程；可运行的教学基线位于独立的 [Labs v0.1.0：Booking Precheck](https://github.com/agentic-styles/labs/tree/v0.1.0/booking-precheck)。Labs 提供 Single-Agent 基线、确定性 Rule Engine、合成样本源文件、Adapter、共享契约和评分工具，PDF 在本地或 CI 从源文件生成。

按[学习教程](tutorial.md)克隆固定版本并完成环境准备后，可以执行离线回归。已验证的范围是离线规则、协议与 scripted 工具循环，不是实际模型准确率；真实 LLM 和 Langfuse 实验需另行配置并运行。Single-Agent 保留教学基线的已知边界，Multi-Agent 是学员需要设计、实现和验证的候选方案，尚未提供完成的参考实现。

课程中的示例指标不能视为 Labs 当前版本的实测结果。没有运行证据时，只提交设计假设和验证计划。构建本课程不读取 Labs，不需要其依赖，也不把它作为 submodule。

所有承运人、航线、规则和单证均为合成教学材料。预审通过不等于危险品分类、最终承运批准或订舱确认。

## 学习入口

- [学习教程与讲师指引](tutorial.md)
- [课程大纲](outline.md)
- [来源与迁移说明](provenance.md)
- [实验工程 README（固定版本）](https://github.com/agentic-styles/labs/blob/v0.1.0/booking-precheck/README.md)

构建后的站点入口为 `lab/index.html`，播放器为同目录 `presentation.html`。构建产物不进入 Git。
