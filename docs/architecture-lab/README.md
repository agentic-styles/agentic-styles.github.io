# Agentic Architecture Lab

面向工程师与架构师的质量属性驱动设计课程。通过合成的 Booking Precheck 场景，学习从业务证据、基线与架构压力出发，选择职责、控制权和协作契约，再用实验作出 Adopt、Adapt 或 Reject 决策。

## 本模块包含什么

- 71 页课程 Slides、可选择的 Optional Detail 与讲师备注。
- 两个可直接讨论的合成案例，以及设计练习和验收门槛。
- 从质量场景、设计手段、Pattern 到接口与 ADR 的推理路径。
- 对统一评测接口、Dataset、Trace 和指标的设计讲解。

## 当前运行边界

当前仓库可以构建和浏览课程，不能直接运行订舱预审 Agent 或重现课程中的指标。它不包含原项目的 Python Agent、PDF 样本集、Rule Engine、Adapter、Langfuse Dataset 同步工具或 Micro Demo。

Slides 中的工具名、协议名和命令名用于解释原参考实现。需要动手运行时，应先准备独立实现与评测环境，并完成教程中的实验准备清单。没有运行证据时，只提交设计假设和验证计划。

所有承运人、航线、规则和单证均为合成教学材料。预审通过不等于危险品分类、最终承运批准或订舱确认。

## 学习入口

- [学习教程与讲师指引](tutorial.md)
- [课程大纲](outline.md)
- [来源与迁移说明](provenance.md)

构建后的站点入口为 `lab/index.html`，播放器为同目录 `presentation.html`。构建产物不进入 Git。
