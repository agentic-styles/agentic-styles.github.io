# 来源与迁移说明

本模块提取自 OOCL AI 2026 私有结项归档中的 Booking Precheck Slides 源码、讲师教程与课程大纲。归档仓库为 `canmor/oocl-ai-2026`，来源提交为 `b7fc04f`。原交付版本继续留在归档中，本模块是后续公开演进的独立课程内容。

本次迁移保留 71 页讲解和播放器的键盘、总览、备注、全屏及 Optional Detail 功能；把固定授课日程改为学习阶段，去除 Day 1/Day 2 包装。课程仓库独立维护讲解，运行工程由 [agentic-styles/labs v0.1.1](https://github.com/agentic-styles/labs/tree/v0.1.1/booking-precheck) 提供，包括教学基线、合成样本源文件、契约与评分工具。

Booking Precheck 的业务规则、承运人、航线和单证均为合成教学材料。所有协议、工具命令和指标应在课程语境下理解；迁移没有重新运行原来的 Agent 实验。

Labs 首版验证限于离线规则、协议和 scripted 工具循环，不构成真实 LLM 准确率结果，也未实现供课程直接比较的 Multi-Agent 方案。课程链接固定到 `v0.1.1/booking-precheck`，但站点构建不获取 Labs 代码、不安装其运行依赖，也不使用 submodule。

未复制真实凭据、环境文件、Git 历史恢复包、运行时数据库、整套评测标准答案或私有归档全文。源代码、可编辑 HTML 模板、教程与大纲进入版本库；HTML、PDF 等发布制品由构建流程生成，不进入版本历史。

原课程的来源说明包括 ISO/IEC 25010:2023、ISO/IEC 25059:2023 和 NIST AI Risk Management Framework。本课程中的架构推导、练习、阈值与案例属于教学设计，不应视为上述标准的正式条文或一致性认证。
