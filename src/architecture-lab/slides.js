/* Agentic Architecture Lab: editable teaching content. Runtime experiments require a separate implementation. */
const SLIDES = [
  {
    "id": "1",
    "part": "A",
    "title": "先看证据，再决定要不要多 Agent",
    "kind": "title",
    "claim": "以合成案例，学习架构设计与验证",
    "visual": "title",
    "agenda": {
      "morning": [
        [
          "01",
          "看懂合成案例与证据链"
        ],
        [
          "02",
          "理解基线与评测边界"
        ],
        [
          "03",
          "识别当前架构压力"
        ]
      ],
      "afternoon": [
        [
          "04",
          "质量属性、Pattern 与 ADR"
        ],
        [
          "05",
          "上下文与协作契约"
        ],
        [
          "06",
          "对比方案并作出决定"
        ]
      ]
    },
    "notes": "课程模块提供 71 页设计讲解和练习，不包含可运行的 Booking Precheck、Langfuse 或 Multi-Agent 实现。先阅读课程首页和教程，再决定只做设计练习，还是自备实现与评测环境开展运行实验。所有案例均为合成教学材料。"
  },
  {
    "id": "2",
    "part": "A",
    "title": "其他条件不变，只换架构",
    "kind": "standard",
    "claim": "这样最后的差异，才可能是架构带来的。",
    "items": [
      "控制变量：业务、案例集、规则、模型和评分方法",
      "允许改变：Agent 分工、上下文、协作方式和失败处理",
      "先跑基线，再设计、实现、比较、决定"
    ],
    "visual": "experiment",
    "notes": "不得修改 Expected Output 或 Evaluator 迁就新实现。"
  },
  {
    "id": "2A",
    "part": "A",
    "title": "每个阶段，都在为最后的决定找证据",
    "kind": "optional",
    "claim": "不是听完概念就结束，而是一路留下可以比较的产出。",
    "items": [
      "看懂业务：画出证据链",
      "跑出基线：记录 Single-Agent 结果",
      "设计架构：写质量场景和 ADR",
      "实现方案：跑出 Multi-Agent 结果",
      "公平比较：使用同一个 Dataset",
      "做决定：采用、调整或放弃"
    ],
    "visual": "journey",
    "notes": "Optional Detail。按学习阶段展开；无需遵循原项目授课日程。"
  },
  {
    "id": "3",
    "part": "A",
    "title": "预审通过，不等于最终批准",
    "kind": "statement",
    "claim": "Booking Precheck 只判断：现有资料能不能进入下一步。",
    "items": [
      "不负责危险品分类",
      "不代表承运人最终批准",
      "更不等于订舱已经确认"
    ],
    "visual": "boundary",
    "notes": "所有承运人、航线、规则和单证均为合成教学材料。"
  },
  {
    "id": "4",
    "part": "A",
    "title": "输入是三份 PDF，不是现成的 JSON",
    "kind": "visual-first",
    "claim": "系统先要读懂不同版式，还要处理缺失和冲突。",
    "items": [
      "Booking Request：客户想订什么",
      "Preliminary DGD：危险品申报了什么",
      "SDS Extract：货物的性质和运输信息"
    ],
    "visual": "documents",
    "notes": "职责边界应回应真实不确定性，而不是只按业务名词拆分。"
  },
  {
    "id": "5",
    "part": "A",
    "title": "每个结论，都要能回到原文",
    "kind": "standard",
    "claim": "状态答对了，但说不清证据在哪里，仍然不合格。",
    "items": [
      "先从 PDF 提取并整理事实",
      "再用 Policy Rule 检查事实",
      "保留所有命中原因，不只保留最终状态",
      "结论要能回到具体文档、页码和原文"
    ],
    "visual": "evidence-chain",
    "notes": "让学员观察回溯线：结论必须能回到文档与 Policy 页码。"
  },
  {
    "id": "5A",
    "part": "A",
    "title": "只给一个状态，远远不够",
    "kind": "optional",
    "claim": "一个可用的结果，还要告诉人和系统接下来怎么办。",
    "items": [
      "最终状态",
      "所有原因和命中的规则",
      "文档证据和 Policy 证据",
      "缺什么、交给谁、下一步做什么",
      "Trace、审计记录和运行指标"
    ],
    "visual": "result-contract",
    "notes": "Optional Detail。对输出契约不熟悉时展开。"
  },
  {
    "id": "5B",
    "part": "A",
    "title": "信息先往上抽象，再沿证据回到原文",
    "kind": "insert",
    "claim": "Document 变成 Fact，Fact 与 Policy 产生 Rule Finding；Evidence 再把判断锚定回具体页码和原文。",
    "items": [
      "Document → Fact：从原始文字和版式，提炼出规范化业务事实",
      "Fact + Policy → Rule Finding：在更高一层做确定性业务判断",
      "Evidence 不是更高一层结论，而是 Rule → Fact → Document 的回溯路径"
    ],
    "visual": "information-abstraction",
    "notes": "Core Insert。这里的“概念晋级”指信息抽象层级，不是 Agent 技术层级。严格来说，Policy 是规则定义；Facts 与 Policy 运算后产生的是 Rule Finding。Evidence 是向下的 Traceability Mapping，把命中规则重新连接到 fact_path、页码和原文。"
  },
  {
    "id": "6",
    "part": "A",
    "title": "一个 UN Number 冲突，会经过四道关",
    "kind": "visual-first",
    "claim": "这不是简单的“模型答错了”，每一层都可能出问题。",
    "items": [
      "Booking 写的是 UN1263",
      "DGD 写的是 UN1866",
      "一致性规则发现冲突",
      "系统转入 MANUAL_REVIEW，交给 DG Desk"
    ],
    "visual": "conflict",
    "notes": "让学员指出错误可能发生在抽取、比较、规则或聚合哪一层。"
  },
  {
    "id": "7",
    "part": "A",
    "title": "90 秒：顺着证据查一遍",
    "kind": "activity",
    "claim": "从教程里的合成案例选一个，顺着证据检查。",
    "items": [
      "你看到了哪些事实？",
      "哪条规则会用到这些事实？",
      "最后是什么状态？下一步做什么？",
      "如果结果错了，你先查哪一层？"
    ],
    "visual": "timer",
    "notes": "教程提供 UN Number 冲突与缺件两个合成案例；不依赖原 Evidence Lab 应用。"
  },
  {
    "id": "8",
    "part": "B",
    "title": "没有基线，就不知道重构有没有用",
    "kind": "statement-split",
    "claim": "“看起来更清楚”和“Agent 更多”，都不是证据。",
    "items": [
      "先记下质量",
      "再记下延迟",
      "也别漏掉成本"
    ],
    "visual": "baseline",
    "notes": "在同一评分方法上比较候选架构；没有实际运行时，只填写假设，不捏造结果。"
  },
  {
    "id": "9",
    "part": "B",
    "title": "Langfuse 把案例、运行和分数串起来",
    "kind": "standard",
    "claim": "我们只需要用好一条最小实验链路。",
    "items": [
      "Dataset 存案例",
      "Task 运行系统，Trace 记录过程",
      "Evaluator 打分，Experiment Run 汇总结果"
    ],
    "visual": "langfuse",
    "notes": "每个概念只解释其在本课程中的角色。"
  },
  {
    "id": "10",
    "part": "B",
    "title": "一个 Dataset Item：题目和标准答案",
    "kind": "visual-first",
    "claim": "系统只拿到输入；标准答案只交给评分器。此处展示数据设计。",
    "items": [
      "输入：pack_id 和 stage_id",
      "业务答案：TC / BA expected.json",
      "文档事实：DP ground-truth.json"
    ],
    "visual": "dataset-item",
    "notes": "标准答案由课程资产提供，不由 Langfuse 或模型生成。"
  },
  {
    "id": "10A",
    "part": "B",
    "title": "标准答案来自两套课程文件",
    "kind": "optional",
    "claim": "一套判断业务结果，一套检查文档事实和证据位置。",
    "items": [
      "expected.json：状态、规则、原因、队列和行动",
      "ground-truth.json：字段值、规范化结果、页码和原文",
      "两套答案一起放进 expected_output"
    ],
    "visual": "answer-sources",
    "notes": "Optional Detail。第一次接触评测数据设计时保留。"
  },
  {
    "id": "11",
    "part": "B",
    "title": "Agent 看不到答案，只通过统一接口运行",
    "kind": "visual-first",
    "claim": "这样 Single-Agent 和 Multi-Agent 才能公平比较。",
    "items": [
      "输入通过 booking-precheck-eval/v1 送给 Agent",
      "标准答案绕过 Agent，直接送给 Evaluator",
      "Agent 统一返回 result、facts 和 telemetry"
    ],
    "visual": "isolation",
    "notes": "这是原教学案例的接口设计示意；当前课程不附带 booking-precheck-eval/v1 的运行实现。Harness 应通过接口而非导入内部实现。"
  },
  {
    "id": "11A",
    "part": "B",
    "title": "Manifest 让评测工具不用了解内部实现",
    "kind": "optional",
    "claim": "评测工具照同一种方式启动不同架构。",
    "items": [
      "Manifest 说明怎么启动 Adapter",
      "请求和响应都使用 JSONL",
      "Single-Agent 和 Multi-Agent 只需要换 Manifest",
      "响应必须包含 result、facts 和 telemetry"
    ],
    "visual": "manifest",
    "notes": "Optional Detail。学员要自行实现 Adapter 时展开。"
  },
  {
    "id": "12",
    "part": "B",
    "title": "API Key 只放本地，别发到聊天或 Git",
    "kind": "statement-split",
    "claim": "任何截图、日志和协作记录里，都不应该出现 Secret。",
    "items": [
      "LANGFUSE_BASE_URL",
      "LANGFUSE_PUBLIC_KEY",
      "LANGFUSE_SECRET_KEY"
    ],
    "visual": "secret",
    "notes": "只展示变量名和 placeholder，不展示真实值。"
  },
  {
    "id": "13",
    "part": "B",
    "title": "五步准备一个可比较的基线",
    "kind": "activity",
    "claim": "本模块讲解实验设计；运行实验需另行准备实现和评测环境。",
    "items": [
      "明确案例集、规则和预期输出",
      "准备 Single-Agent 实现与统一输入输出接口",
      "先验证一个端到端案例",
      "冻结案例版本和评分方法",
      "记录基线的质量、延迟与成本"
    ],
    "visual": "runbook",
    "notes": "当前仓库可运行的是静态课程构建与播放器，不包含 Agent Adapter、模型调用或 Langfuse Dataset 同步命令。教程给出设计练习和实验准备清单。"
  },
  {
    "id": "13A",
    "part": "B",
    "title": "先检查一个端到端案例",
    "kind": "optional",
    "claim": "Doctor 是原案例的检查工具；也可以采用等价的环境检查。",
    "items": [
      "选一个输入完整的合成案例",
      "确认任务完成状态可观察",
      "输出必须包含 result、facts 和 telemetry",
      "先验证接口，再扩大案例集"
    ],
    "visual": "terminal",
    "notes": "Optional Detail。现场故障较多时展开。"
  },
  {
    "id": "13B",
    "part": "B",
    "title": "用稳定 ID 同步，重复运行也不会多出数据",
    "kind": "optional",
    "claim": "同步方案示例：同一个 Stage 写回同一个 Dataset Item。",
    "items": [
      "预先定义稳定的案例与 Stage ID",
      "同步后核对案例数量和版本",
      "Stable ID → Upsert → 不产生重复 Item"
    ],
    "visual": "sync",
    "notes": "Optional Detail。Dataset 已预置时可跳过。"
  },
  {
    "id": "13C",
    "part": "B",
    "title": "案例集里的每一项，都跑同一个 Task",
    "kind": "optional",
    "claim": "任务定义不变；执行器遍历同一版本的 Dataset Items。",
    "items": [
      "为基线记录独立的 Run Name",
      "每个 Item 都有对应 Trace 和评分",
      "并发度属于实验配置，需要记录并保持比较口径"
    ],
    "visual": "experiment-items",
    "notes": "原案例集含 9 个 Stage；当前课程没有附带该运行环境。不要将 JSONL Client 的限制解释为 Langfuse 的能力限制。"
  },
  {
    "id": "14",
    "part": "B",
    "title": "哪一步失败，就先查哪一层",
    "kind": "standard",
    "claim": "不要把所有错误都归到 Langfuse 或模型。",
    "items": [
      "离线测试失败：查 Contract 和 Harness",
      "Doctor 失败：查 Manifest、Adapter、模型或 PDF",
      "Sync 失败：查 Langfuse 登录和 Dataset",
      "Experiment 失败：查 9 个 Item、Task 和 Evaluator"
    ],
    "visual": "diagnostic-ladder",
    "notes": "避免把模型连接错误误诊为 Langfuse 错误。"
  },
  {
    "id": "15",
    "part": "B",
    "title": "分数会告诉我们：问题出在哪一类",
    "kind": "visual-first",
    "claim": "把“效果不好”拆成质量、安全和效率三个问题。",
    "items": [
      "质量：状态、规则、字段和证据是否正确",
      "安全：系统有没有跑完，会不会错误放行",
      "效率：花了多久、调用几次模型、用了多少 Token"
    ],
    "visual": "score-bands",
    "notes": "functional_pass 是严格复合门槛，不等于最终状态正确。"
  },
  {
    "id": "16",
    "part": "B",
    "title": "示例：状态正确，证据仍可能不完整",
    "kind": "visual-first",
    "claim": "演示数据只说明如何读指标，不能作为新方案的验证结果。",
    "items": [
      "Technical · 100%",
      "Status · 100%",
      "Field · 97.9%",
      "Evidence · 66.7%",
      "P95 · 25.8s",
      "Avg Calls · 4.56"
    ],
    "visual": "scoreboard",
    "notes": "这些数字来自原授课材料中的参考展示，当前模块未重新运行核验。它们不是固定阈值、公共 benchmark 或架构收益证明；实际实验应填入自己的测量结果。"
  },
  {
    "id": "17",
    "part": "B",
    "title": "别只看平均分，打开一条失败 Trace",
    "kind": "standard",
    "claim": "平均分告诉你有问题，Trace 才告诉你问题在哪里。",
    "items": [
      "先从 Run 找到失败 Item",
      "再看 Scores 和实际输出",
      "最后沿 Trace 找到具体步骤",
      "DP-006：字段全对，但证据仍然缺失"
    ],
    "visual": "trace",
    "notes": "设计练习可用教程中的合成 Trace 讨论；运行实验时保存真实 Run URL 和指标。当前模块不提供线上 Trace。"
  },
  {
    "id": "18",
    "part": "C",
    "title": "一个看过程，一个做对比",
    "kind": "standard",
    "claim": "LangSmith 帮你看单次运行，Langfuse 帮你比较多轮实验。",
    "items": [
      "LangSmith Studio：看流程、状态和工具调用",
      "Langfuse：看案例集、实验分数和版本差异"
    ],
    "visual": "two-tools",
    "notes": "两种工具是可替换的教学示例，不是本课程的运行依赖。"
  },
  {
    "id": "19",
    "part": "C",
    "title": "一个 Agent 管全程",
    "kind": "visual-first",
    "claim": "Single-Agent 里，什么时候读、什么时候调用工具、什么时候结束，都由同一个 Agent 决定。",
    "items": [
      "PDFs → initialize_case",
      "precheck_agent 和 precheck_tools 反复协作",
      "最后由 finalize_result 收尾"
    ],
    "visual": "single-loop",
    "notes": "展示 Single-Agent 参考结构；实际运行需自备对应实现与环境。"
  },
  {
    "id": "20",
    "part": "C",
    "title": "State 要记录业务进展，不只是聊天消息",
    "kind": "visual-first",
    "claim": "Messages 用来协调；业务事实和结果要单独保存。",
    "items": [
      "Documents → Facts",
      "Required Evidence → Matches",
      "Aggregate → Final Result"
    ],
    "visual": "state-layers",
    "notes": "为后续 Shared Case State 的所有权与合并机制铺垫。"
  },
  {
    "id": "20A",
    "part": "C",
    "title": "Tools 把“读懂”连接到“按规则判断”",
    "kind": "optional",
    "claim": "Agent 负责理解，工具负责把结果写入确定的业务流程。",
    "items": [
      "提交事实",
      "执行规则",
      "提交证据",
      "查询 Policy",
      "生成最终结果"
    ],
    "visual": "tools",
    "notes": "Optional Detail。用于判断哪些能力可被多个 Agent 复用。"
  },
  {
    "id": "21",
    "part": "C",
    "title": "LLM 负责理解，确定性组件负责裁决",
    "kind": "visual-first",
    "claim": "最终状态不能由 LLM 或 Orchestrator 随意改写。",
    "items": [
      "LLM：阅读、整理事实、组织证据、选择工具",
      "Tool / Node：校验格式、计算、跑规则、定优先级、留审计记录",
      "Final Status 必须留在确定性一侧"
    ],
    "visual": "deterministic-boundary",
    "notes": "明确不可破坏的裁决边界。"
  },
  {
    "id": "22",
    "part": "C",
    "title": "Single-Agent 简单，但压力也在增加",
    "kind": "standard",
    "claim": "它不是错误答案，而是我们要用证据挑战的基线。",
    "items": [
      "好处：协调少、容易运行、结构简单",
      "压力：上下文越来越大，一个失败会影响整票",
      "压力：证据工作混在一起，出错后不容易定位"
    ],
    "visual": "tension",
    "notes": "每组写下一个有代码或 Trace 证据的压力。"
  },
  {
    "id": "23",
    "part": "D",
    "title": "先说清问题，再选 Pattern",
    "kind": "statement",
    "claim": "范围 → 质量目标 → 具体场景 → 架构压力 → 设计手段 → 职责 → 实验",
    "items": [],
    "visual": "decision-chain",
    "notes": "进入轻量 ADD；不展开完整 ADD、Utility Tree 或 ATAM。"
  },
  {
    "id": "24",
    "part": "D",
    "title": "功能一样，不代表架构质量一样",
    "kind": "standard",
    "claim": "“我想用这个 Pattern”只是偏好，不是设计理由。",
    "items": [
      "功能：系统要做什么",
      "质量：遇到冲突、失败、变更或负载时，做得怎么样",
      "约束：哪些条件不能改",
      "偏好：团队喜欢哪种技术或 Pattern"
    ],
    "visual": "four-statements",
    "notes": "技术偏好不能伪装成质量属性。"
  },
  {
    "id": "24A",
    "part": "D",
    "title": "先全面查漏，再选最重要的三个质量目标",
    "kind": "insert",
    "claim": "这三层视角帮我们发现问题，不替我们做优先级决定。",
    "items": [
      "软件产品质量：参考 ISO/IEC 25010",
      "AI 可信性：参考 ISO/IEC 25059 和 NIST AI RMF",
      "Agent 执行质量：看行动、上下文、协作和控制",
      "最后仍要根据业务压力和基线证据选 Top 3"
    ],
    "visual": "quality-lenses",
    "notes": "Core Insert。三层不是三个必选篮子，仍以业务目标、压力与 Baseline Evidence 排序。"
  },
  {
    "id": "24B",
    "part": "D",
    "title": "ISO 帮我们统一说法，AI 框架帮我们补漏",
    "kind": "optional",
    "claim": "这些模型告诉我们要看哪些方向，但不会替项目写验收标准。",
    "items": [
      "ISO/IEC 25010:2023：通用的软件产品质量",
      "ISO/IEC 25059:2023：补充 AI 系统质量",
      "NIST AI RMF：关注可靠、安全、韧性、透明、可解释、隐私和公平",
      "不要把不同框架的术语硬做一一对应"
    ],
    "visual": "standards",
    "notes": "Optional Detail。ISO 25059 正在修订以对齐 25010:2023。",
    "sources": [
      "https://www.iso.org/standard/78176.html",
      "https://www.iso.org/standard/80655.html",
      "https://www.nist.gov/itl/ai-risk-management-framework"
    ]
  },
  {
    "id": "24C",
    "part": "D",
    "title": "看 Agent 系统，重点检查这六件事",
    "kind": "insert",
    "claim": "这是课程里的检查清单，不是新的行业标准。",
    "items": [
      "结果对不对",
      "工具调用和行动靠不靠谱",
      "上下文和状态会不会丢或串",
      "Agent 之间交接是否清楚",
      "控制和失败处理是否安全",
      "成本、速度和排错是否可接受"
    ],
    "visual": "agentic-lens",
    "notes": "Core Insert。这是课程透镜，不是行业标准。"
  },
  {
    "id": "25",
    "part": "D",
    "title": "没有“最好”的架构，只有适不适合当前场景",
    "kind": "statement-split",
    "claim": "架构只能创造有利条件，真正结果还取决于模型、工具和实现。",
    "items": [
      "架构决定职责和协作",
      "Prompt 和模型影响理解与生成",
      "工具和代码守住确定性边界",
      "四者一起决定最终结果"
    ],
    "visual": "outcome",
    "notes": "禁止无条件声称 Multi-Agent 更 scalable 或更可靠。"
  },
  {
    "id": "26",
    "part": "D",
    "title": "把模糊要求写成能测试的场景",
    "kind": "visual-first",
    "claim": "“要更快、更稳”不够，必须说明谁、何时、对什么、做到什么程度。",
    "items": [
      "谁触发（Source），发生了什么（Stimulus）",
      "系统哪一部分被影响（Artifact），当时是什么环境（Environment）",
      "系统怎么响应（Response），做到什么程度（Measure）"
    ],
    "visual": "scenario",
    "notes": "重点纠正缺失 Artifact，以及 Stimulus / Environment 混淆。"
  },
  {
    "id": "26A",
    "part": "D",
    "title": "“低延迟”要这样写，才能真的测",
    "kind": "optional",
    "claim": "把一句愿望展开成一条可以直接运行的实验。",
    "items": [
      "谁触发：Booking Intake",
      "发生什么：收到三份完整单证",
      "测哪里：端到端 Workflow",
      "什么环境：模型服务正常",
      "系统做什么：完成抽取、规则和证据整理",
      "怎么达标：9-DP 的 P95 不高于基线"
    ],
    "visual": "scenario-example",
    "notes": "Optional Detail。会写场景的班级可直接进入练习。"
  },
  {
    "id": "27",
    "part": "D",
    "title": "架构选择一定会有取舍",
    "kind": "visual-first",
    "claim": "如果一个方案只有好处没有代价，我们多半还没看清它。",
    "items": [
      "更低延迟 ↔ 更仔细的复核",
      "更清楚的职责 ↔ 更多协调工作",
      "更细的 Trace ↔ 更多 Token 和存储成本"
    ],
    "visual": "tradeoffs",
    "notes": "不展示所谓最佳位置。"
  },
  {
    "id": "28",
    "part": "D",
    "title": "练习：先选三个目标，再谈需要几个 Agent",
    "kind": "activity",
    "claim": "先决定最想改善什么，再决定怎么拆。",
    "items": [
      "每个人先列候选目标",
      "小组合并并排出 Top 3",
      "把每个目标写成六要素场景",
      "为场景补上基线证据",
      "准备向全班说明为什么这样排"
    ],
    "visual": "top3",
    "notes": "约 25 分钟。禁止把“使用多 Agent”写成质量属性。"
  },
  {
    "id": "29",
    "part": "D",
    "title": "好场景既能指导设计，也能验证结果",
    "kind": "activity",
    "claim": "同一张 Worksheet 会在设计前后各用一次。",
    "items": [
      "写清场景和优先级",
      "补齐六个要素",
      "标出对应的基线证据",
      "检查：能测吗？有没有偷塞解决方案？有没有取舍？"
    ],
    "visual": "worksheet",
    "notes": "每组 2–3 分钟；超过 5 组采用 Lightning Showcase。"
  },
  {
    "id": "29A",
    "part": "D",
    "title": "不合适的架构会阻碍质量目标实现",
    "kind": "insert",
    "claim": "架构不合适，质量目标很难达成；架构合适，也不能保证结果。",
    "items": [
      "职责、边界、数据流或失败隔离不匹配，会放大延迟、耦合和故障",
      "合适的架构只是创造必要条件，不能自动产生质量结果",
      "最终仍要用刚才写好的场景和指标验证"
    ],
    "visual": "quality-realization",
    "notes": "Core Insert。承接质量属性场景写作，再进入设计。先讲阻碍作用，再讲必要不充分：架构失配时很难达标，结构合理也不会自动带来目标结果。"
  },
  {
    "id": "30",
    "part": "E",
    "title": "别从质量目标直接跳到 Pattern",
    "kind": "visual-first",
    "claim": "中间还要想清楚设计手段、职责边界和接口。",
    "items": [
      "先找关键质量目标（Driver）",
      "再选设计手段（Tactic）",
      "根据设计手段划分职责",
      "最后才落到 Pattern 和接口"
    ],
    "visual": "driver-chain",
    "notes": "阻止直接套 Pattern。"
  },
  {
    "id": "31",
    "part": "E",
    "title": "串行、统一调度和按需路由，解决的是不同问题",
    "kind": "visual-first",
    "claim": "先看 Top Driver，再排除不合适的协作方式。",
    "items": [
      "Pipeline：步骤有先后，容易调试，但并行少",
      "Orchestrator–Workers：统一调度多个专家，但协调器更复杂",
      "Router–Specialists：只叫需要的专家，但可能路由错或漏掉"
    ],
    "visual": "patterns-a",
    "notes": "只讲小组实际考虑的候选，避免逐项念定义。"
  },
  {
    "id": "32",
    "part": "E",
    "title": "多一层复核，通常也会多一层成本",
    "kind": "visual-first",
    "claim": "任何额外协作，都要说清它到底改善了哪个目标。",
    "items": [
      "Parallel Reviewers：独立复核，但结果可能冲突",
      "Generator–Reviewer：一人生成、一人检查，但更慢更贵",
      "Shared State：逐步补充状态，但更难管清谁能修改"
    ],
    "visual": "patterns-b",
    "notes": "课堂不采用复杂 Swarm 或去中心化 P2P。"
  },
  {
    "id": "33",
    "part": "E",
    "title": "Agent 可以拆，规则和最终裁决不能乱拆",
    "kind": "visual-first",
    "claim": "按 Booking、DGD、SDS 拆 Agent，必须有明确的质量理由。",
    "items": [
      "只有为了并行、隔离失败、应对变化或独立测试，才值得拆",
      "Agent 负责理解和整理证据",
      "Schema、计算、规则、聚合和评分保持确定性"
    ],
    "visual": "responsibilities",
    "notes": "Final Decision 始终留在确定性边界。"
  },
  {
    "id": "34",
    "part": "E",
    "title": "接口要写失败怎么处理，ADR 要写什么时候放弃",
    "kind": "standard",
    "claim": "没有失败条件和否决条件，设计就无法真正接受验证。",
    "items": [
      "接口写清：职责、输入、输出、协作和失败行为",
      "ADR 写清：背景、决定、备选、代价和验证方法",
      "备选方案必须包括保留 Single-Agent",
      "编码前就写好 Reject Conditions"
    ],
    "visual": "adr-interface",
    "notes": "Failure 与 Reject Conditions 是本页重点。"
  },
  {
    "id": "34A",
    "part": "E",
    "title": "在写代码前，先写下“什么情况算失败”",
    "kind": "optional",
    "claim": "实验的目的不是证明我们对，而是允许架构假设被否决。",
    "items": [
      "为什么需要改变",
      "决定采用什么方案",
      "还考虑过哪些方案，包括 Single-Agent",
      "准备承担哪些代价",
      "什么证据支持采用，什么证据要求放弃"
    ],
    "visual": "adr",
    "notes": "Optional Detail。正式提交 ADR 的班级保留。"
  },
  {
    "id": "35",
    "part": "E",
    "title": "设计练习：把三个质量目标变成可实现架构",
    "kind": "activity",
    "claim": "最后的设计要清楚到足以交给 AI Coding。",
    "items": [
      "比较两个候选 Pattern",
      "分配职责，写清输入输出",
      "画出谁调用谁、谁负责合并",
      "写下 ADR 和否决条件",
      "用 3 分钟说明设计理由"
    ],
    "visual": "design-task",
    "notes": "巡检边界是否来自 Driver，而不是业务名词。"
  },
  {
    "id": "36",
    "part": "E",
    "title": "开始编码前，先回答这六个问题",
    "kind": "activity",
    "claim": "Architecture Design Gate",
    "items": [
      "每个 Agent 为什么需要单独存在？",
      "它改善哪个质量目标？",
      "它最少需要哪些输入？",
      "谁负责最终状态？",
      "它失败时会不会错误放行？",
      "用哪个 Score 判断它有没有用？"
    ],
    "visual": "six-questions",
    "notes": "Showcase 后进入 Micro Demo，暂不允许提前编码。"
  },
  {
    "id": "37",
    "part": "F",
    "title": "设计理由已经写好，现在看代码怎么协作",
    "kind": "statement",
    "claim": "ADR 解释为什么这样拆，协作流程图说明拆完后怎样推进。",
    "items": [
      "先回到自己的 ADR",
      "沿任务、结果与共享状态检查协作",
      "准备好实现环境后，再把机制写进代码"
    ],
    "visual": "adr-demo-code",
    "notes": "当前模块提供协作机制的图示与讲解，不附带可运行的 Micro Demo。"
  },
  {
    "id": "38",
    "part": "F",
    "title": "给单个 Agent 的上下文，不等于整个案件状态",
    "kind": "standard",
    "claim": "每个 Agent 只拿需要的信息，完整业务状态由系统统一维护。",
    "items": [
      "Agent Context：这个 Worker 本次工作需要的最小输入",
      "AgentResult：Worker 返回的不可变结果",
      "Shared Case State：系统合并后的完整业务状态",
      "Messages：只记录局部协调过程"
    ],
    "visual": "scope",
    "notes": "澄清四类数据的作用域。"
  },
  {
    "id": "39",
    "part": "F",
    "title": "最小协作闭环：发任务、收结果、统一合并",
    "kind": "visual-first",
    "claim": "Worker 只产出局部结果，Reducer 负责检查和合并。",
    "items": [
      "Coordinator 生成 AgentTask",
      "Worker 返回 AgentResult",
      "Reducer 合并到 Shared Case State"
    ],
    "visual": "task-result-reducer",
    "notes": "沿 Fake Worker 的输入、返回值和 Reducer 合并路径做桌面推演；代码实验需自行实现。"
  },
  {
    "id": "40",
    "part": "F",
    "title": "Task 限制输入，Result 统一输出",
    "kind": "visual-first",
    "claim": "可以附上自然语言说明，但不能只靠自然语言交接。",
    "items": [
      "AgentTask：案件、目标、文档引用和需要的输出",
      "AgentResult：状态、事实、证据、错误和 Telemetry",
      "任务里绝不能带 Ground Truth 或完整聊天历史"
    ],
    "visual": "contracts",
    "notes": "讲解 Handoff Contract。"
  },
  {
    "id": "40A",
    "part": "F",
    "title": "AgentTask 就是一张“允许带入”的清单",
    "kind": "optional",
    "claim": "Worker 只接收完成当前职责所需的最少信息。",
    "items": [
      "task_id 和 case_id：这是哪个任务、哪个案件",
      "objective：这次要完成什么",
      "document_refs 和 required_outputs：读什么、交什么",
      "不能带入完整 Messages 或 Ground Truth"
    ],
    "visual": "task-schema",
    "notes": "Optional Detail。实现 Worker 输入 Schema 前展开。"
  },
  {
    "id": "40B",
    "part": "F",
    "title": "成功或失败，都返回 AgentResult",
    "kind": "optional",
    "claim": "这样 Reducer 才能统一处理，也能看见失败发生在哪里。",
    "items": [
      "成功时返回 status、facts、evidence 和 telemetry",
      "失败时返回 status、error 和 telemetry",
      "不能只抛一个异常就结束",
      "失败结果也要进入统一合并流程"
    ],
    "visual": "result-schema",
    "notes": "Optional Detail。避免 Worker 失败时只抛异常。"
  },
  {
    "id": "41",
    "part": "F",
    "title": "只有 Reducer 能写共享状态",
    "kind": "visual-first",
    "claim": "Worker 只提交结果，不能互相覆盖，也不能直接改 Shared State。",
    "items": [
      "每个 Worker 追加一份不可变结果",
      "Reducer 负责校验、去重、分区和合并",
      "Shared Case State 只有一个明确的 Owner"
    ],
    "visual": "reducer",
    "notes": "对比共享可变 Dict 带来的竞态与覆盖风险。"
  },
  {
    "id": "42",
    "part": "F",
    "title": "一个 Worker 失败，系统也不能错误放行",
    "kind": "visual-first",
    "claim": "只要关键结果不完整，就不能得到 PRECHECK_PASS。",
    "items": [
      "Worker 超时或返回 Failed Result",
      "Shared State 标记为不完整",
      "系统选择失败、重试或升级人工",
      "绝不能为了继续流程而假装成功"
    ],
    "visual": "fail-safe",
    "notes": "主线只要求失败安全，不扩展完整恢复流程。"
  },
  {
    "id": "43",
    "part": "F",
    "title": "把自己的 ADR 填进这张上下文表",
    "kind": "activity",
    "claim": "用五分钟，把设计变成可以直接编码的输入输出边界。",
    "items": [
      "有哪些 Agent 或 Node",
      "每个角色可以收到什么、不能收到什么",
      "每个角色要产出什么",
      "谁拥有和修改 State",
      "失败时怎么处理"
    ],
    "visual": "context-table",
    "notes": "检查 Coordinator、Reducer 和失败传播。"
  },
  {
    "id": "44",
    "part": "G",
    "title": "AI 可以加快编码，但架构决定仍由小组负责",
    "kind": "standard",
    "claim": "AI 能写实现，不能替团队决定边界、风险和取舍。",
    "items": [
      "让 AI 帮忙：代码骨架、类型、节点、Reducer、Adapter 和测试",
      "小组负责：职责边界、上下文、State Owner、失败处理和验收",
      "如果 AI 的建议偏离 ADR，小组必须判断并记录原因"
    ],
    "visual": "ai-boundary",
    "notes": "建立 AI Coding 边界。"
  },
  {
    "id": "45",
    "part": "G",
    "title": "用三轮 Prompt，把设计一步步写成代码",
    "kind": "visual-first",
    "claim": "先让 AI 理解设计，再小步实现，最后根据真实错误修复。",
    "items": [
      "第一轮：把 ADR 和上下文表变成实施计划",
      "第二轮：分步实现 Task、Result、State、Reducer 和 Adapter",
      "第三轮：运行测试与端到端检查，根据真实报错修改"
    ],
    "visual": "three-prompts",
    "notes": "三轮迭代指向可评估 Thin Slice。"
  },
  {
    "id": "46",
    "part": "G",
    "title": "AI 不能改评分标准，也不能偷看答案",
    "kind": "statement-split",
    "claim": "这些不是建议，而是代码审查时必须检查的红线。",
    "items": [
      "不修改 Expected、Evaluator 或 Rule 的含义",
      "Ground Truth 不能进入 Agent",
      "关键 Worker 失败时不能返回 Pass",
      "不要把完整 Context 无脑复制给所有 Agent"
    ],
    "visual": "redlines",
    "notes": "代码审查优先检查数据流与评测文件变更。"
  },
  {
    "id": "47",
    "part": "G",
    "title": "先做一个能运行、能评测的最小版本",
    "kind": "activity",
    "claim": "先跑通最小闭环，不要急着把每个细节都做完。",
    "items": [
      "Gate 1：Task → Result 契约闭环",
      "Gate 2：单案例可通过 Reducer 合并",
      "Gate 3：环境检查通过，冻结的案例集可启动"
    ],
    "visual": "gates",
    "notes": "实现阶段建议；本课程不含该实现。没有可运行环境时，完成设计和验收计划即可，不应宣称通过运行 Gate。"
  },
  {
    "id": "48",
    "part": "H",
    "title": "多 Agent 也要跑同一套 Dataset",
    "kind": "visual-first",
    "claim": "除了 Manifest 和 Run Name，其他条件都不变。",
    "items": [
      "使用同一个 Dataset",
      "模型档位和 Policy Snapshot 不变",
      "使用同一组 Evaluator",
      "只把 Single-Agent Task 换成 Multi-Agent Task"
    ],
    "visual": "same-dataset",
    "notes": "不得创建更容易的新 Dataset 或跳过失败 Item。"
  },
  {
    "id": "49",
    "part": "H",
    "title": "重点看改了多少，不要只看最后分数",
    "kind": "standard",
    "claim": "每个 Top Driver 都要能对应到一个指标或人工测量。",
    "items": [
      "并排看 Single、Multi 和 Delta",
      "质量和安全有没有改善",
      "延迟、调用次数和 Token 增加了多少",
      "排错时间是否缩短，是否支持原来的质量目标"
    ],
    "visual": "comparison",
    "notes": "使用 6–8 行低密度对比。"
  },
  {
    "id": "50",
    "part": "H",
    "title": "一个坏案例，往往比平均分更能说明问题",
    "kind": "visual-first",
    "claim": "选一个最能解释架构差异的案例，追到根因。",
    "items": [
      "先对照 Expected、Actual 和 Scores",
      "再沿 Trace 找到负责的 Agent 或 Tool",
      "最后说明根因和架构之间有什么关系"
    ],
    "visual": "bad-case",
    "notes": "突出 Single / Multi 在同一 Item 上的差异。"
  },
  {
    "id": "51",
    "part": "H",
    "title": "五分钟汇报，只讲这五件事",
    "kind": "activity",
    "claim": "Architecture Defense",
    "items": [
      "最重要的三个质量目标",
      "选择的 Pattern 和职责边界",
      "Langfuse 分数发生了什么变化",
      "一个最能说明问题的坏案例",
      "最后决定：采用、调整还是放弃"
    ],
    "visual": "showcase",
    "notes": "限制架构图讲解，重点放在数据与取舍。"
  },
  {
    "id": "52",
    "part": "H",
    "title": "采用、调整、放弃，都可以是好结论",
    "kind": "visual-first",
    "claim": "成功不是“证明 Multi-Agent 更好”，而是用证据做出可信决定。",
    "items": [
      "Adopt：收益成立，代价可以接受",
      "Adapt：方向有用，但职责或协作还要调整",
      "Reject：收益太小，或者代价太高"
    ],
    "visual": "three-exits",
    "notes": "必须引用 ADR 中预先定义的 Validation / Reject Conditions。"
  },
  {
    "id": "53",
    "part": "H",
    "title": "做到这些，架构实验才算完成",
    "kind": "activity",
    "claim": "同一把尺、能运行、能解释。",
    "items": [
      "Single-Agent Baseline Run",
      "三个质量属性场景",
      "ADR 和上下文表",
      "可运行的 Multi-Agent Adapter",
      "同一 Dataset 的 Multi-Agent Run",
      "一个坏案例和最终决定"
    ],
    "visual": "dod",
    "notes": "仅做本模块的设计练习时，交付场景、ADR、上下文表和验证计划；只有实际运行后，才能提交 Run、测量和最终实验证据。"
  },
  {
    "id": "54",
    "part": "H",
    "title": "架构是假设，不是 Agent 数量比赛",
    "kind": "statement-split",
    "claim": "先说清想改善什么，再设计怎么协作，最后让同一套证据决定值不值得改。",
    "items": [
      "Single-Agent 给出基线",
      "Multi-Agent 提出假设",
      "数据决定采用、调整还是放弃"
    ],
    "visual": "final",
    "notes": "以每组一句最终建议收尾，不使用通用 Thank You 页。"
  }
];

const PARTS = {
  "A": "看懂 Booking Precheck 的证据",
  "B": "跑出 Single-Agent 基线",
  "C": "看懂当前架构的优点和压力",
  "D": "用质量属性做架构决定",
  "E": "选 Pattern、分职责、写 ADR",
  "F": "把 Multi-Agent 协作跑起来",
  "G": "用 AI 辅助重构",
  "H": "用同一套数据做最后判断"
};
