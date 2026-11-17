# 学习教程与讲师指引

## 先选择学习方式

设计练习：只需浏览 Slides 和本教程，输出质量属性场景、职责图、ADR、上下文表和验证计划。这条路径不依赖模型 API 或外部服务。

运行实验：使用独立的 [Labs v0.1.0 实验工程](https://github.com/agentic-styles/labs/tree/v0.1.0/booking-precheck)，其中提供 Single-Agent 教学基线、合成输入、冻结规则、共享契约和确定性评分器。候选 Multi-Agent 架构仍需自行实现；只有完成实际测量，才能评价架构收益。本仓库只提供课程，不嵌入或安装运行工程。

## 获取固定版本并运行离线回归

先安装 Git、uv 和 Python 3.12，再从一个独立工作目录执行以下命令。课程固定使用 `v0.1.0`，便于复现；后续 Labs 版本应独立评审后再更新课程链接。

```sh
git clone --branch v0.1.0 https://github.com/agentic-styles/labs.git
cd labs/booking-precheck
uv sync --all-packages --all-extras --locked
uv run --locked python tools/generate_materials.py
uv run --locked python -m pytest contracts/tests agent/tests evaluation/tests
uv run --locked booking-precheck-eval run --config evaluation/configs/deterministic-smoke.json --output-dir .generated/evaluation
uv run --locked python ../scripts/verify_evaluation.py .generated/evaluation
```

依赖安装需要访问软件包源。材料生成、以上测试与确定性 smoke 不需要模型密钥，不调用真实模型或 Langfuse。PDF 从受版本控制的合成源文件生成，评测报告保存在 `.generated/evaluation/`；生成物不进入 Git。

离线测试验证规则、协议、PDF 解析及 scripted 模型驱动的生产工具循环，不测量真实 LLM 准确率。确定性 smoke 运行基线和评分链路；某些提取指标因基线仅返回结果而显示 `N/A`，不能据此推断模型表现。该版本没有完成的 Multi-Agent 方案。

首版的 51 次确定性调用均成功，规则 30/30、业务 12/12 通过；文档阶段仅 2/9 功能通过，其余 7 项被评分器判为文档证据不完整。Labs 的回归检查明确保留这些已知缺口，并检查新增失败；CI 通过不等于所有质量目标已满足。

模型实验、Langfuse 配置与教学基线边界见 [Labs README](https://github.com/agentic-styles/labs/blob/v0.1.0/booking-precheck/README.md)。只有明确配置并选择相应命令后，才运行这些外部服务实验；不要把离线测试通过率或课件中的数字当作真实模型结论。

## 学习路径

1. 看懂业务证据：文档如何变成事实，事实如何消费规则，结论如何回溯原文。
2. 定义基线：先明确正确性、失败安全、证据完整性、延迟和成本的测量口径。
3. 识别架构压力：区分读取错误、事实错误、规则错误与聚合错误。
4. 写出质量场景：明确来源、刺激、环境、系统对象、响应与可测量标准。
5. 比较候选方案：选择能回应压力的设计手段、职责边界、Pattern 和接口。
6. 明确协作契约：限制每个 Worker 的上下文，让 Reducer 统一合并结果。
7. 做最小实现：先打通单案例，再运行冻结的案例集。
8. 比较并决定：记录 Delta、失败案例和代价，允许 Adopt、Adapt 或 Reject。

## 合成案例 A：UN Number 冲突

Booking Request 的货物字段写着 `UN1263`；Preliminary DGD 写着 `UN1866`。假设两处文字都已正确读取，可信度也足够。

预审规则要求两份单证的 UN Number 一致。这个案例应转为 `MANUAL_REVIEW`，交由 DG Desk 核对。它不证明哪一个值才是真实货物分类；Agent 不能为了让规则通过而自行覆盖冲突值。

请逐步写下：两个源文档片段、两个独立事实及来源、命中的一致性规则、最终状态和下一步行动。讨论每一层可能出现的错误，以及追查错误所需的证据。

## 合成案例 B：缺少 Preliminary DGD

Booking Request 和 SDS Extract 已提供，Preliminary DGD 未提供。规则要求危险品预审具备 DGD，因此需要 `REQUIRE_INFORMATION` 并请求补件。

缺件不能抹掉已发现的其他问题。如果同时命中更高优先级的阻断规则，最终状态应遵循确定性的状态优先级，同时保留所有原因。不要让某个 Worker 的成功结果覆盖其他 Worker 的缺失或失败。

## 设计练习的最小交付

- 一条可回溯的证据链。
- 三个按重要性排序的质量属性场景。
- 至少两个候选方案，包含保留 Single-Agent 的方案。
- 职责、控制权、状态所有权和失败传播图。
- ADR：背景、选择、备选、代价、验证方法和否决条件。
- Context Contract：每个角色的允许输入、禁止输入、输出、State Owner 与失败行为。
- 验证计划：案例集、评分口径、需要的遥测和停止条件。

## 运行实验前的准备清单

准备可公开或获授权使用的合成单证、字段事实和标准答案。把标准答案放在评测器侧，不能放进 Agent Context。冻结业务规则、聚合语义和预期输出，避免为了候选方案修改评分标准。

使用 Labs 中的共享契约，让 Single-Agent 与候选架构可由同一个 Harness 调用。接口称为 `booking-precheck-eval/v1`，使用 JSONL 传递请求和响应；契约与可执行评测命令位于 Labs，本站只讲解其设计与使用。

为每个案例记录完成状态、最终业务状态、字段与证据质量、延迟、模型调用次数和 Token。成本可用固定价格表换算，但必须记录模型与计价版本。Langfuse 与 LangSmith 是可选的参考工具；也可以使用等价的离线评分和 Trace 记录。

先确认一个端到端案例，再扩大到冻结的案例集。并发、重试、模型配置和超时策略必须记录；若它们是架构方案的一部分，也应在解释收益与代价时明确说明。不能只比较一个没有配置背景的总分。

## 讲师备课

先用 Core-only 模式走完主线，再决定哪些 Optional Detail 需要展开。逻辑 ID 如 `2A` 与物理页码不同，讲课时以页脚 ID 定位。可通过 N 打开讲师备注，O 打开总览，F 切换全屏。

用三分钟讲清课程立场：Multi-Agent 是待验证的架构假设，不是要求学员证明的正确答案。拒绝一个收益不足的方案，同样可以是成功的实验结论。

试讲时完成案例 A 的五分钟证据链讲解、一个质量场景、一次职责与控制权说明，并演示失败时为什么不能错误返回 `PRECHECK_PASS`。

如果没有独立实验环境，应把运行环节改成桌面推演，明确区分输入、假设、预期结果与实测结果。不要把课件中的示例指标当作新实验的测量。

## 指标与证据的解释边界

Slides 的指标页保留了原材料中的演示数字，用于说明“状态正确但证据不完整”的读法。它们未在这次迁移中重新运行核验，不是公共 benchmark，也不是 Multi-Agent 收益证明。

只有数据、代码、模型、配置、案例版本、测量过程和失败记录可追溯时，才提交有条件的实验结论。明确列出仍未验证的质量场景和适用边界。
