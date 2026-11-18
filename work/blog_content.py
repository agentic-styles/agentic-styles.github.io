BLOG = {
    "title": "Agentic AI 系统中的 Pattern：分类、组合与选择",
    "short_title": "Agentic AI 系统中的 Pattern",
    "subtitle": "基于 System of Interest 的三层分析框架，解释 Agentic Pattern 的分类依据、组合关系和架构选择方法。",
    "description": "系统阐述 Agentic AI 中的 Application、Architecture、Design 三层 Pattern 分类依据、跨层组合、结构差异与架构权衡，并区分 Pattern 与实现手段。",
    "author": "Agentic Pattern Atlas Project",
    "published": "2026-08-08",
    "modified": "2026-11-18",
    "version": "2.1",
    "reading_time": "约 30 分钟",
}


READING_PATHS = [
    ("分类框架", "研究问题、System of Interest 与三层分类", "#classification"),
    ("架构组合与选择", "企业异常处置案例、结构比较与架构权衡", "#case"),
    ("参考图鉴", "查阅完整模式目录与来源", "atlas.html"),
]


ANCHOR_IDS = [
    "embedded-copilot",
    "single-agent-system",
    "workflow-centric-hybrid",
    "router-specialist",
    "supervisor-specialist",
    "handoff",
    "fan-out-subagents",
    "magentic-orchestration",
    "react-agent",
    "plan-and-execute",
    "evaluator-optimizer",
    "context-engineering",
    "agentic-rag",
    "durable-agent-workflow",
    "human-in-loop",
]


CASE_STEPS = [
    {
        "layer": "L1",
        "question": "谁承担业务责任？",
        "choice": "Embedded Copilot",
        "reason": "业务处理人员保留异常事件与最终处置责任，Agent 负责分析和建议。",
    },
    {
        "layer": "L2",
        "question": "谁控制整体执行？",
        "choice": "Workflow-Centric Hybrid + Supervisor",
        "reason": "确定性门禁包住概率性诊断，Supervisor 协调业务记录、规则和领域专家。",
    },
    {
        "layer": "L3",
        "question": "Agent 怎样决定下一步？",
        "choice": "ReAct + Plan-and-Execute + Evaluator",
        "reason": "诊断依赖环境反馈；处置需要显式计划；执行前需要独立检查。",
    },
    {
        "layer": "ENABLERS",
        "question": "Pattern 依靠什么实现？",
        "choice": "Context + MCP + Trace / Evals",
        "reason": "组装当前信息、连接外部能力并保留可追踪的质量与运行证据；RAG 与 HITL 已作为 L3 Design Pattern。",
    },
]


COMPARISONS = [
    {
        "id": "control-ownership",
        "title": "Router、Supervisor 与 Handoff",
        "lead": "三种拓扑都可能画成一个 Agent 指向另一个 Agent。真正的差异不是箭头方向，而是箭头之后谁拥有下一步。",
        "columns": ["Pattern", "决定什么", "持续控制者", "会话与目标所有者", "结果如何处理", "主要风险"],
        "rows": [
            ["Router", "一次选择处理者", "原调用方或 Workflow", "原调用方", "目标返回处理结果", "错误分类进入错误路径"],
            ["Supervisor", "反复拆解、委派与汇总", "Supervisor", "Supervisor", "Specialist 多次返回局部结果", "中央瓶颈与压缩失真"],
            ["Handoff", "转移下一步与会话责任", "目标 Agent", "目标 Agent", "继续完成或按协议交回", "上下文丢失与返回路径不明"],
        ],
        "summary": "只需要选一次去向，用 Router；需要跨多轮协调，用 Supervisor；专业 Agent 应接管用户关系时，用 Handoff。",
    },
    {
        "id": "sequence-identity",
        "title": "Prompt Chaining 与 Sequential Agents",
        "lead": "图形上的顺序相同，不代表架构语义相同。关键问题是：每个节点只是一次调用，还是拥有局部目标与决策权的自治单元？",
        "columns": ["维度", "Prompt Chaining", "Sequential Agents"],
        "rows": [
            ["System of Interest", "L3 局部设计", "L2 Agentic System"],
            ["节点身份", "一次 LLM 或工具调用", "拥有局部目标的 Agent"],
            ["步骤来源", "设计时固定", "顺序可固定，节点内部自主执行"],
            ["工具与局部循环", "通常没有或很有限", "可规划、调用工具、维护状态并终止"],
            ["交接内容", "结构化输出", "目标、上下文、状态或控制权"],
            ["协调成本", "低", "高"],
        ],
        "summary": "如果节点不需要独立目标、工具循环、局部记忆或停止条件，就不要把一次模型调用升级成 Agent。",
    },
    {
        "id": "parallel-lifecycle",
        "title": "Parallelization、Parallel Agents 与 Fan-Out",
        "lead": "并发只说明时间关系，不自动说明分支是否拥有 Agent 身份，也不说明它们能否在执行途中通信。",
        "columns": ["Pattern", "本质", "分支身份", "生命周期", "中途通信", "结果回收"],
        "rows": [
            ["Parallelization", "局部并发执行", "调用，不要求 Agent 身份", "单次调用", "通常没有", "Fan-in、投票或聚合"],
            ["Parallel Agents", "多个自治单元同时工作", "稳定或明确的 Agent 角色", "由系统设计决定", "可有可无", "聚合者组合结果"],
            ["Fan-Out Subagents", "动态派发一次性子 Agent", "临时 Agent", "Spawn → Run → Wait → End", "不支持中途纠偏", "主 Agent 批量等待"],
        ],
        "summary": "Fan-Out 可以实现 Parallel Agents；前者强调生命周期和回收，后者描述组织语义。",
    },
    {
        "id": "subagent-lifecycle",
        "title": "Schmid 的四种 Subagent Pattern",
        "lead": "从 Inline 到 Teams，增加的不是简单的 Agent 数量，而是生命周期、通信能力和协调权的逐级迁移。",
        "columns": ["Pattern", "生命周期", "并发", "追加任务", "成员互聊", "协调者", "适合"],
        "rows": [
            ["Inline Tool", "一次性；可同步或异步返回", "无内建 Fan-Out；异步时可与主 Agent 工作重叠", "否", "否", "主 Agent", "单个边界清楚的委派任务"],
            ["Fan-Out", "一次性、异步", "是", "否", "否", "主 Agent", "多个相互独立任务"],
            ["Agent Pool", "持久会话", "是", "是", "不要求", "主 Agent", "需要反复追问的专家"],
            ["Teams", "持久团队", "是", "是", "是", "团队内部", "协调逻辑本身复杂的任务"],
        ],
        "summary": "Inline 与 Fan-Out 的关键差异，是 spawn 与 collect 是否分离、何时 wait 是否由主 Agent 控制；再向 Pool 与 Teams 演进，才逐步引入持久身份、追加任务和成员通信。",
    },
    {
        "id": "protocol-capability",
        "title": "MCP、A2A 与 Agent Skills",
        "lead": "三者都可能被描述为扩展 Agent 能力，但它们连接的对象、任务所有权与生命周期完全不同。",
        "columns": ["维度", "MCP", "A2A", "Agent Skills"],
        "rows": [
            ["连接对象", "Host ↔ Tool/Resource Server", "Agent ↔ Remote Agent", "Host ↔ 可复用能力包"],
            ["核心契约", "Tools、Resources、Prompts", "AgentCard、Message、Task、Artifact", "SKILL.md、脚本、资料与资产"],
            ["执行所有权", "Host Agent 保留任务", "Remote Agent 执行被委派任务", "Host 加载方法并本地使用"],
            ["生命周期", "请求与能力会话", "可支持长任务和状态更新", "按需发现、加载和执行"],
            ["不回答的问题", "多 Agent 如何组织", "采用 Supervisor 还是 Handoff", "Agent 如何连接工具或组织协作"],
        ],
        "summary": "MCP 解决能力连接，A2A 解决远程 Agent 互操作，Skills 解决程序性知识封装；三者都不能替代控制拓扑设计。",
    },
    {
        "id": "adaptive-orchestration",
        "title": "Supervisor、Group Chat 与 Magentic",
        "lead": "三者都可能动态调用多个专家，但共享对象、控制中心与计划形成方式不同。",
        "columns": ["维度", "Supervisor", "Group Chat", "Magentic"],
        "rows": [
            ["持续控制者", "中央 Supervisor", "Chat Manager 管理轮次", "Magentic Manager 管理任务账本"],
            ["主要共享对象", "总目标与专家返回", "累积会话线程", "目标、计划、进度与阻塞账本"],
            ["专家间可见性", "默认隔离", "共享全部讨论", "通过账本共享工作状态"],
            ["计划如何形成", "Supervisor 隐式决定", "讨论中逐步形成", "显式建立并持续修订"],
            ["最适合", "跨域委派与综合", "讨论、创意和联合复核", "开放、长时且路径未知的任务"],
            ["主要风险", "中央瓶颈", "上下文膨胀与轮次循环", "反复重规划但不收敛"],
        ],
        "summary": "已知如何拆解且只需中央综合，用 Supervisor；协作过程本身重要，用 Group Chat；方法与计划也需要在运行中共同发现，用 Magentic。",
    },
    {
        "id": "retrieval-control",
        "title": "Classic RAG 与 Agentic RAG",
        "lead": "两者都把外部证据交给模型，但真正的分界是检索决策在设计时固定，还是由 Agent 在运行时闭环控制。",
        "columns": ["维度", "Classic RAG", "Agentic RAG"],
        "rows": [
            ["检索触发", "每次请求固定执行", "Agent 判断是否需要"],
            ["查询计划", "一个预定义查询变换", "动态分解成多个子查询"],
            ["数据源选择", "设计时固定", "按任务和中间证据选择"],
            ["迭代", "通常一次检索", "评价充分性后继续检索"],
            ["优势", "简单、低延迟、易评估", "复杂问题覆盖与证据发现能力强"],
            ["主要风险", "召回不足直接限制答案", "循环、成本、延迟与不可信证据传播"],
        ],
        "summary": "能够用稳定的一次检索解决，就保留 Classic RAG；只有查询路径和证据充分性确实需要运行时推理时，才升级为 Agentic RAG。",
    },
]


DECISION_QUESTIONS = [
    ("01", "谁拥有最终目标与失败责任？", "先确定 L1。若人保留最终责任，优先考虑 Copilot 或显式业务流程，而不是默认后台自治。"),
    ("02", "谁决定下一步，控制权是否转移？", "一次分派看 Router，持续协调看 Supervisor，接管会话看 Handoff。"),
    ("03", "哪些状态必须共享，哪些上下文必须隔离？", "共享越多，单 Agent 越有吸引力；权限、专业知识或上下文需要隔离时，才增加 Agent 边界。"),
    ("04", "不使用更高自治结构时，具体损失是什么？", "只有并行收益、独立权限、领域隔离或上下文容量带来明确价值时，才升级到更复杂的组织。"),
]


SELECTED_SOURCE_IDS = [
    "iso-42010",
    "adp-official",
    "anthropic-agents",
    "schmid-subagents",
    "ms-architecture",
    "ms-workflows",
    "lang-subagents",
    "lang-router",
    "lang-handoffs",
    "react-paper",
    "mcp-architecture",
    "a2a-spec",
    "agent-skills-spec",
    "google-agent-patterns",
    "ms-agent-orchestration",
    "ms-durable-agent",
    "ms-agentic-rag",
    "aws-event-orchestration",
    "ms-agent-identity",
]
