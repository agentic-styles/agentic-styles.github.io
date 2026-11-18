"""Formal explanatory prose for the Atlas article.

The Pattern catalog remains in atlas_data.py; these passages are original
editorial synthesis. Links use the public Atlas entry IDs as stable anchors.
"""

TABLE_OF_CONTENTS = [
    ("problem", "问题与研究范围"),
    ("classification", "分类依据"),
    ("map", "三层分类框架"),
    ("enablers", "Pattern 与 Enabler"),
    ("case", "跨层组合案例"),
    ("comparisons", "模式结构比较"),
    ("decision", "选择与架构权衡"),
    ("conclusion", "结论"),
]

INTRO = """
<div class="article-text">
<h3>不同性质的概念被混作同一选项</h3>
<p>Agentic AI 系统的设计涉及业务责任、系统组织、局部执行和技术连接等不同性质的决策。然而，ReAct、Multi-Agent、RAG、MCP、Supervisor 与 Workflow 等术语经常并列出现在方案比较中。以企业异常处置助手为例，讨论有时会从「使用 ReAct、Multi-Agent、RAG 还是 MCP」开始。这一问题没有形成有效的比较关系，因为所列概念回答的不是同一个设计问题。</p>
<p><a href="atlas.html#react-agent">ReAct</a> 描述推理、行动与观察之间的局部反馈循环；Multi-Agent 是涵盖多种组织结构的系统范畴，并非单一模式；<a href="atlas.html#rag">RAG</a> 描述知识检索参与生成的结构，其检索控制还可能进一步演化为 <a href="atlas.html#agentic-rag">Agentic RAG</a>；<a href="atlas.html#mcp">MCP</a> 则规范 Host 与外部工具、资源等能力之间的连接方式。这些概念可以出现在同一套系统中，没有必要强行择一。</p>
<p>例如，业务人员可以在既有应用中使用 Copilot，后台以工作流控制审批门禁，某个阶段由 Supervisor 调度领域 Agent；各个 Agent 可以通过 ReAct 决定工具调用，检索企业知识库，并由 MCP Client 连接工具服务。不同的决定分别改变了业务责任、系统控制、局部行为和集成方式。</p>
<h3>分类的目的不是统一所有术语</h3>
<p>这种混淆首先是分析边界的问题。仅知道一个方案包含「三个 Agent」或「使用某款 Agent 框架」，仍无法判断谁拥有任务目标、谁决定下一步、控制权能否转移以及失败应由谁处理。相反，明确这些结构问题后，即使采用不同产品和技术栈，也可以对两个设计做有意义的比较。</p>
<p>本文提出一个基于 <strong>System of Interest</strong> 的三层分析框架：L1 Application Pattern、L2 Architecture Pattern 和 L3 Design Pattern。它用于澄清概念、比较结构与指导组合，而不声称提供行业强制分类标准。与三层 Pattern 相区别的协议、技术、能力格式和工程实践作为 Enabler 单独讨论。完整条目及来源见<a href="atlas.html">视觉图鉴</a>，正文重点解释分类与架构决策的推理过程。</p>
</div>
"""

CLASSIFICATION = """
<div class="article-text">
<h3>2.1 System of Interest 决定分析范围</h3>
<p>System of Interest（SoI）指当前架构讨论所关注的系统。一次分析可以将整套业务应用视为系统，也可以将其中的 Agentic 子系统视为系统，或进一步关注某个 Agent 的局部执行机制。选定对象之后，才可以区分系统内部的责任关系与对外部环境的交互。</p>
<p>以异常订单处置为例：在业务应用范围内，问题是员工与智能助手如何划分审查和批准责任；在 Agentic 子系统范围内，问题变成工作流与多个专家 Agent 如何协同；在某个诊断 Agent 的范围内，问题则是何时检索、调用工具、检查证据及停止循环。同一个产品可以同时包含这三种结构，但它们不能通过单一「Agent 数量」指标来概括。</p>
<p>本文借鉴 ISO/IEC/IEEE 42010 对关注对象及架构描述的思路。该标准采用更宽泛的 Entity of Interest 概念；<strong>本文的 L1/L2/L3 不是该标准规定的层次</strong>，也不应误解为符合该标准所必需的架构步骤。</p>
<h3>2.2 Pattern 识别依赖结构关系及控制语义</h3>
<p>Pattern 不是技术名称的集合。一个候选 Pattern 至少应描述可复用的问题情境、参与者或角色、它们之间具有意义的关系，以及这种结构为什么产生预期收益与代价。在 Agentic 系统中，静态连接线尤其不足以表达结构：相似的「Agent A → Agent B」可能分别代表一次路由、持续委派或会话所有权交接。</p>
<p>本文重点观察六个维度。<strong>目标与责任所有权</strong>确定谁对最终结果负责；<strong>控制权</strong>确定谁决定下一步以及是否转移；<strong>自治边界</strong>确定哪些单元能够独立规划、行动并终止；<strong>状态与上下文</strong>确定数据如何持有、共享或隔离；<strong>生命周期</strong>区分单次调用、临时 Agent 与持久职责；<strong>协作机制</strong>说明委派、同步、通信、汇总和失败处理。并非所有维度都适合区分每一个 Pattern，应选择对当前问题真正有判别力的维度。</p>
<h3>2.3 分类不是部署结构，也不是固定流水线</h3>
<p>三层主要反映 <em>所关注的结构决策</em>，不是进程、服务、机器或模型实例的层数。一个进程内可以实现多个自治 Agent；分布式服务也可能仅支撑单个 Agent 的工具执行。系统采用什么框架，同样不能直接决定其 Pattern 分类。</p>
<p>部分设计具有跨层影响。例如 Human-in-the-Loop 在业务层涉及最终授权责任，在局部流程中则表现为暂停、批准与恢复的控制结构。本文按照讨论的 SoI 归类具体设计问题，不认为一个术语在所有情境下都只能出现于唯一层级。L1、L2、L3 也不是必须自上而下走完一次的开发阶段：局部实现的风险和成本，可以反过来推动系统架构或业务自治范围的修订。</p>
</div>
"""

LEVELS = """
<div class="article-text">
<h3>3.1 L1 — Agentic Application Pattern</h3>
<p>L1 关注 Agent 在业务应用及社会技术责任体系中的位置：由谁发起任务，谁持有业务目标，哪些决定需要人工批准，Agent 的授权范围持续多久。它决定的是 Agent 如何参与业务，而不是 Agent 自身采用哪种推理算法。</p>
<p>在 <a href="atlas.html#embedded-copilot">Embedded Copilot</a> 中，Agent 增强既有业务应用，业务人员保留任务和最终决定；在 <a href="atlas.html#workflow-participant">Agentic Workflow Participant</a> 中，Agent 承担业务流程中的受限活动，流程仍由既有机制控制；<a href="atlas.html#agentic-front-door">Agentic Front Door</a> 则提供跨业务域的统一交互入口。对比之下，<a href="atlas.html#autonomous-worker">Autonomous Agent Worker</a> 可以在明确授权和停止条件内执行后台任务，而 <a href="atlas.html#always-on-agent-worker">Always-on Agent Worker</a> 增加持续委托和跨运行连续性。<a href="atlas.html#continuous-controller">Continuous Sense-Decide-Act Controller</a> 的关键则是根据行动结果反复调节业务状态，而不只是定期被唤醒。</p>
<p>这些模式即使使用完全相同的 LLM 和工具，其风险与治理要求也可能截然不同。Copilot 的主要风险可能是建议质量和人员审查负担；常驻自主工作者还必须处理权限失效、重复触发、跨运行状态漂移与撤销授权。因此，应先明确业务责任与允许的自治范围，再确定内部系统结构。</p>
<h3>3.2 L2 — Agentic Architecture Pattern</h3>
<p>L2 关注 Agentic System 的整体组织：整体目标由谁持有，任务如何拆分，执行顺序由显式 Workflow 还是 Agent 在运行时决定，多个参与者如何共享状态、交换结果并处理失败。<strong>L2 并不等于 Multi-Agent</strong>，因为一个 Agent 的系统组织方式同样是架构决定。</p>
<p><a href="atlas.html#single-agent-system">Single-Agent System</a> 将规划、工具选择和结果整合集中到一个 Agent，减少协调成本，却可能增加上下文与权限复杂度；<a href="atlas.html#workflow-centric-hybrid">Workflow-Centric Hybrid</a> 由显式流程保留关键顺序、分支和门禁，只在需要不确定性判断的环节调用 Agent。前者适合任务关联紧密、上下文共享价值高的场景，后者更适合可审计、可恢复的业务过程。</p>
<p>在多个专业处理者的设计中，<a href="atlas.html#router-specialist">Router-Specialist</a> 负责选择去向而不持续管理全局目标；<a href="atlas.html#supervisor-specialist">Supervisor-Specialist</a> 则持续委派、观察与汇总；<a href="atlas.html#handoff">Handoff</a> 将下一步控制权及相关上下文交给目标 Agent。其他模式如 <a href="atlas.html#group-chat">Group Chat</a>、<a href="atlas.html#magentic-orchestration">Magentic Orchestration</a>、<a href="atlas.html#event-choreography">Event Choreography</a> 和 <a href="atlas.html#shared-blackboard">Shared Blackboard</a>，进一步区分共享会话、动态任务账本、事件传播和共享工作空间等协作机制。</p>
<p>增加 Agent 不一定改善架构。如果专业职责不明确，或多个参与者必须频繁共享完整上下文，多 Agent 设计可能只增加通信延迟、失败路径与调试难度。L2 的评判标准应是系统控制与协调结构能否更好地满足实际约束。</p>
<h3>3.3 L3 — Agentic Design Pattern</h3>
<p>L3 关注既定系统边界内如何组织局部决策、行动、反馈与恢复。<a href="atlas.html#react-agent">ReAct</a> 通过推理、行动和环境观察的循环动态决定下一步；<a href="atlas.html#plan-and-execute">Plan-and-Execute</a> 区分计划与执行；<a href="atlas.html#evaluator-optimizer">Evaluator-Optimizer</a> 以评价反馈推动候选输出迭代改进。它们分别针对环境交互、计划可检查性和结果质量控制。</p>
<p>L3 也包含更确定性的结构，例如 <a href="atlas.html#prompt-chaining">Prompt Chaining</a> 的固定步骤、<a href="atlas.html#parallelization">Parallelization</a> 的局部并发，以及 <a href="atlas.html#human-in-loop">Human-in-the-Loop</a> 的审批门禁。<a href="atlas.html#rag">RAG</a> 与 <a href="atlas.html#agentic-rag">Agentic RAG</a> 的区别在于检索步骤及证据充分性判断是否由运行时 Agent 进行动态控制；两者不是系统级编排的替代品。</p>
<p>一个 Supervisor 管理的专业 Agent 可以使用 ReAct 和 RAG，另一个专家可以采用固定的 Prompt Chaining。由此可见，L3 的局部设计与 L2 的协作结构能够组合，而不必统一成一种模式。</p>
<h3>3.4 层次之间的约束与反馈</h3>
<p>三个层级可以理解为相互关联的架构决定：L1 的授权与业务责任对 L2 的控制结构提出约束；L2 的任务组织决定哪些 L3 行为是必要的；L3 的不确定性、工具权限、延迟与恢复成本又可能反馈到更高层。在业务要求人工批准退款的情况下，L1 的责任约束可以促使 L2 引入显式审批门禁，并要求 L3 支持暂停、保留证据和恢复执行。分类提供的是分析视角，而不是预先固定的实现顺序。</p>
</div>
"""

ENABLERS = """
<div class="article-text">
<h3>4.1 结构决定与实现能力应分别描述</h3>
<p>Architecture Pattern 与 Design Pattern 的作用是定义可重复的角色、关系、控制结构及其代价。Enabler 则提供实现这些结构所需的协议、技术、能力格式或工程实践。二者不是「抽象技术」和「具体技术」的简单二分：一些局部设计同样会被多个架构重用，能够复用本身不能证明某项概念只是 Enabler。</p>
<p>判断一项概念是否属于 Pattern，应先问它是否规定了能够独立辨识的参与者与控制关系；再问它主要回答的是「怎样组织这个系统」还是「怎样让已选择的结构获得某种能力」。例如 Supervisor 规定持续协调者与专家之间的目标和结果关系，而 MCP 不规定系统应该由一个还是多个 Agent 控制，也不规定工作流何时需要人工审批。因此 MCP 属于协议层面的 Enabler，而不是第四层架构。</p>
<h3>4.2 三种常见能力连接机制</h3>
<p><a href="atlas.html#mcp">MCP</a> 主要标准化 Host 与 Tool、Resource、Prompt 服务之间的交互；<a href="atlas.html#a2a">A2A</a> 提供远程 Agent 的发现、任务交换与状态协作契约；<a href="atlas.html#agent-skills">Agent Skills</a> 将指令、脚本和参考资料封装为可发现、可加载的程序性能力包。三者解决的互操作问题不同，均无法直接回答系统采用 Router、Supervisor 还是 Handoff。即便使用 A2A 连接两个远程 Agent，也还需要明确任务目标、会话所有权和失败责任。</p>
<p>同样，<a href="atlas.html#context-engineering">Context Engineering</a> 负责为模型与工具调用组装必要上下文，<a href="atlas.html#evaluation-monitoring">Evaluation and Monitoring</a> 负责检验结果并观察运行行为，<a href="atlas.html#guardrails">Guardrails and Safety</a> 提供风险限制与执行检查。这些机制可以横向支撑 L1 的治理约束、L2 的协作结构和 L3 的局部行为。它们具有架构重要性，但不应取代对结构的说明。</p>
<p>实施时应把「选用何种 Pattern」与「以哪些协议或工程机制实现它」分别记录在架构决策中。这有助于在保留控制结构的前提下更换技术实现，也有助于防止协议选型被误当作业务责任和自治边界的决策。</p>
</div>
"""

CASE = """
<div class="article-text">
<h3>5.1 从业务约束而不是技术栈出发</h3>
<p>考虑一个用于企业订单异常诊断与处置的说明性场景：订单状态、履约记录和客户反馈互相矛盾，系统需要检索交易记录与规则，识别可能的原因、准备证据并提出处置建议。退款、状态修改与外部通知等有业务影响的动作必须由员工审查批准。这里的业务目标不是「尽可能自主」，而是在保持责任与审计链条清晰的前提下减少调查工作量。</p>
<p>第一项决定属于 L1：使用 <a href="atlas.html#embedded-copilot">Embedded Copilot</a>，让员工持有异常处置目标与最终审批责任。这样可以将 Agent 的权限限定为调查、比较和提出建议，而不是让后台自治工作者直接完成所有业务动作。</p>
<h3>5.2 将控制权划分为确定性骨架与概率性诊断</h3>
<p>第二项决定属于 L2：采用 <a href="atlas.html#workflow-centric-hybrid">Workflow-Centric Hybrid</a> 管理证据收集、审批、写回和审计等有明确顺序的环节；其中需要跨业务域调查的步骤，可以由 <a href="atlas.html#supervisor-specialist">Supervisor-Specialist</a> 协调订单、履约和规则专家。Workflow 负责流程门禁与可恢复性，Supervisor 负责诊断任务的动态委派和综合。两者并不争夺同一个最终控制权：Supervisor 的自治范围被限制在 Workflow 允许的阶段内。</p>
<p>这一选择不是唯一实现。若证据来源少且上下文能够安全共享，Single-Agent System 可能足够；若异常类型稳定、一次分类就能确定专家，Router-Specialist 可能比 Supervisor 成本更低。选择 Supervisor 的条件应是调查确实需要反复委派和跨域综合，而不只是存在多个业务接口。</p>
<h3>5.3 为局部行为配置模式与保障</h3>
<p>第三项决定属于 L3：诊断 Agent 可以用 <a href="atlas.html#react-agent">ReAct</a> 根据查询结果决定下一次调用，以 <a href="atlas.html#plan-and-execute">Plan-and-Execute</a> 显式呈现处置步骤，并通过 <a href="atlas.html#evaluator-optimizer">Evaluator-Optimizer</a> 或独立证据检查识别未经证实的假设。知识来源可以由 RAG 提供，具有业务影响的动作则必须经过 <a href="atlas.html#human-in-loop">Human-in-the-Loop</a> 门禁。这里的评价与人工审批作用不同：自动评价检查输出质量，审批决定是否授权业务操作。</p>
<p>最后才选择 Enabler：Context Engineering 将订单、历史事件和权限上下文组织成可用输入；MCP 可以连接受控工具；Trace、Evals 与策略检查记录诊断依据、工具调用和审批结果。协议与评估设施支持所选结构，但不能单独提供业务授权。</p>
<h3>5.4 组合关系及其边界</h3>
<p>下图同时标出 L1、L2、L3 与 Enabler，表达的是结构决定之间的关系，而不是四个必须按顺序执行的运行步骤。应用层对退款审批的要求能够约束整个系统；局部 Agent 的工具错误也必须被工作流捕获并可追踪。由此，跨层组合需要一致的任务标识、权限边界、失败语义和审计记录，不能只把几张拓扑图拼接起来。</p>
</div>
"""

COMPARISONS_INTRO = """
<div class="article-text">
<p>两个方案即使画出相同的箭头，也可能具有不同的责任与控制语义。比较 Pattern 时应先识别共同问题，再找到足以改变运行行为的结构差异，最后分析这些差异如何影响状态、异常恢复、延迟和成本。下面的表格保留具体维度，文字说明则突出各组模式为何不能仅凭外观归类。</p>
<h3>6.1 目标所有权与控制权转移</h3>
<p>Router、Supervisor 与 Handoff 的共同点是把工作交给专门的处理者；区别在于分派之后谁决定下一步。Router 选择处理者，调用方或 Workflow 仍对整体流程负责。Supervisor 持续拥有整体目标，能够重复调用专家并整合结果。Handoff 把下一步会话或任务控制权转给目标 Agent。错误地将 Handoff 当作普通工具调用，容易使接管、返回和审计路径缺失。</p>
</div>
"""

COMPARISONS_ADAPTIVE = """
<div class="article-text">
<p>持续协调也不只存在 Supervisor 一种形式。Group Chat 通过共享会话线程组织参与者轮次，适合交互过程本身重要的协作；Magentic Orchestration 将计划、进度与阻塞记录为显式工作账本，适合开放且路径难以事先确定的工作。与集中式 Supervisor 相比，它们需要处理更复杂的共享状态、收敛判断和执行预算。</p>
<h3>6.2 Agent 身份、并行关系与生命周期</h3>
<p>顺序执行并不意味着每个步骤都是自治 Agent。Prompt Chaining 的每个节点通常是事先确定的模型或工具调用，而 Sequential Agents 中的节点拥有独立的局部目标、工具循环或状态。并发也不意味着产生了持久 Agent：一次性 Parallelization、多个稳定的 Parallel Agents 和临时 Fan-Out Subagents 在通信能力、等待时机和故障隔离上各不相同。</p>
</div>
"""

COMPARISONS_LIFECYCLE = """
<div class="article-text">
<p>Subagent 的生命周期使这种差异更加明确。Inline Tool 适合一次受限委派；Fan-Out 将多个一次性任务异步派发并集中等待；Agent Pool 支持复用持久会话与追加任务；Teams 进一步引入成员之间的持续通信。随着自治单元从一次性调用演化为持续协作，系统获得灵活性，也增加了调度、状态一致性与故障处理成本。</p>
<h3>6.3 局部检索的控制权</h3>
<p>Classic RAG 和 Agentic RAG 都使用外部证据，但前者通常采用固定检索路径，后者允许 Agent 动态决定查询、数据源以及是否继续检索。只有当检索路径和证据充分性确实依赖运行时判断时，迭代检索才值得承担额外的延迟、成本和不确定性。因此，对比模式的目标不是给出「更先进」的排名，而是识别哪些结构能力为当前问题所必需。</p>
</div>
"""

DECISION = """
<div class="article-text">
<h3>7.1 将选择转化为可检验的设计决定</h3>
<p>Pattern 选择应从需求约束而非术语流行度出发。首先确定业务目标和关键操作的责任归属，继而明确谁控制执行、哪些状态必须共享、哪些权限必须隔离。之后为候选结构设定可比较的场景与质量属性，例如任务完成率、错误审批风险、恢复时间、交互延迟、运行成本、证据追溯能力以及后续维护负担。</p>
<p>对不同候选方案，不应仅比较正常路径。在异常订单场景中，应特别检验证据缺失、工具超时、模型产生未经证实结论、员工拒绝审批、任务中途恢复等条件。若某方案需要多个 Agent 才能满足领域权限隔离，这是增加复杂度的可解释理由；若单 Agent 已能达到质量目标，则多 Agent 的协调成本不一定值得。</p>
<h3>7.2 最小必要自治与最小必要协调</h3>
<p>在满足需求的候选中，优先考虑能够实现目标的最小必要自治和协调结构。这不是排斥高级模式，而是将其引入与可观察收益绑定：例如并行化改善了关键路径延迟，独立 Agent 边界减少了敏感上下文暴露，或 Supervisor 在多轮跨域任务中明显提高了完成率。</p>
<p>更高自治通常还要求更严格的停止条件、预算、权限撤销、幂等控制、失败恢复、可观测性与回归评估。质量属性之间也存在权衡：更多验证与人工门禁会增加延迟，却可能减少高风险操作错误；更深的 Agent 自治会提高开放任务适应能力，却增加结果重现与解释难度。</p>
<h3>7.3 记录假设、证据与剩余风险</h3>
<p>可以把一次架构选择记录为：<strong>问题与约束 → 候选 Pattern → 结构差异与质量属性假设 → 可观察的验证场景 → 选择及剩余风险</strong>。如采用 Supervisor，应写明哪些任务需要反复委派，如何衡量其收益，以及为什么 Router 或 Single-Agent System 不足。架构决策的依据应随着原型、评估和生产证据更新，而不是将 Pattern 名称视为永久正确的答案。</p>
</div>
"""

CONCLUSION = """
<div class="article-text">
<p>Agentic AI 的架构分析应首先明确所讨论的 System of Interest，再识别决定业务责任、整体组织和局部行为的结构关系。L1 Application Pattern 关注 Agent 如何参与业务及承担什么责任；L2 Architecture Pattern 关注系统如何组织任务与分配控制权；L3 Design Pattern 关注局部推理、行动、反馈和门禁如何实现。协议、能力格式及工程实践能够支撑这些结构，但不能替代结构决策。</p>
<p>这一框架的价值不在于提供唯一的 Pattern 分类答案，而在于使候选方案可以被有依据地比较与组合。ReAct 不能替代 Supervisor，MCP 不能替代 Handoff，RAG 也不决定谁对业务结果负责。架构设计仍然需要在自治、可靠性、安全、延迟、成本与可维护性之间进行显式权衡，并用场景与证据验证。</p>
<p>本文分类是一种可修订的工程分析方法，并非统一行业标准。完整的 Pattern 拓扑、适用信号、变体、来源和详细权衡由<a href="atlas.html">Agentic Pattern Atlas</a> 持续维护；本篇文章则提供理解和使用该图鉴的分类逻辑与决策方法。</p>
</div>
"""

METHOD = """
<div class="article-text">
<p><strong>分类方法。</strong> 本文依据 System of Interest、责任所有权、控制权、自治边界、状态、生命周期与协作关系对已公开的 Pattern 和相关技术进行综合分析。三层模式与独立 Enabler 目录属于本项目归纳，不代表 ISO/IEC/IEEE 42010 或其他组织发布的统一分层标准。</p>
<p><strong>术语与来源。</strong> 图鉴区分「来源原名」「规范化命名」与「本文归纳」。条目来源支持参与者、结构和术语的描述；应用条件、成本、失败模式和跨层影响在未另行注明时属于本文分析。《Agentic Design Patterns》的引用统一指向 Springer 的正式出版版本和相应章节；协议细节应以供应方发布的具体规范版本为准。</p>
<p><strong>案例与图表。</strong> 企业异常处置为说明性设计推导，不是已验证的生产部署。所有架构拓扑是项目为解释结构重新绘制的图示，不表示必须采用某种进程、部署或供应商实现。Pattern 目录内容可能随领域发展变化，本文应优先保持分类判据与决策逻辑的稳定。</p>
</div>
"""

ARTICLE_CSS = r"""
/* Article reading rhythm: prose carries the argument; diagrams and tables support it. */
.blog-page .hero h1{max-width:16ch;font-size:clamp(2.8rem,5.5vw,6.3rem);line-height:1.11}
.blog-page .hero h1 small{display:block;max-width:35ch;margin-top:1.5rem;font-family:var(--sans);font-size:clamp(.85rem,1.2vw,1.12rem);font-weight:500;line-height:1.6;letter-spacing:0}
.article-toc{padding:clamp(2.5rem,5vw,5rem) max(5vw,calc((100vw - 1380px)/2));background:var(--paper-2);border-bottom:1px solid var(--rule)}
.article-toc h2{font-family:var(--serif);font-size:clamp(1.8rem,3vw,2.6rem);margin:0 0 1.4rem}
.article-toc ol{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0;margin:0;padding:0;list-style:none;border-top:2px solid var(--ink)}
.article-toc li{border-bottom:1px solid var(--rule);border-right:1px solid var(--rule)}
.article-toc li:nth-child(4n){border-right:0}
.article-toc a{display:flex;align-items:baseline;gap:.75rem;padding:1rem .85rem;text-decoration:none;font-size:.83rem}
.article-toc b{font-family:var(--serif);color:var(--muted);font-size:1rem}
.article-text{max-width:78ch;margin:2rem 0 3rem}
.article-text h3{font-family:var(--serif);font-size:clamp(1.35rem,2.1vw,1.95rem);line-height:1.34;margin:2.5rem 0 1.15rem}
.article-text p{font-size:clamp(1rem,1.15vw,1.12rem);line-height:1.95;margin:1rem 0 1.5rem;max-width:78ch}
.article-text a{color:inherit;text-decoration:underline;text-decoration-color:var(--muted);text-decoration-thickness:1px;text-underline-offset:3px}
.case-section .article-text a,.conclusion-section .article-text a{color:#e6f2ed;text-decoration-color:#bad7d5}
.article-text strong{font-weight:750}
.article-text em{font-style:italic}
.article-level-map{margin:2.4rem 0 3rem}
.article-level-map figcaption,.case-figure figcaption{max-width:90ch;line-height:1.7}
.article-comparison-theme{max-width:78ch;margin:2.6rem 0 2.2rem}
.article-comparison-theme h3{font-family:var(--serif);font-size:clamp(1.5rem,2.3vw,2.2rem);margin:0 0 1rem}
.article-comparison-theme p{line-height:1.9;font-size:1rem}
.article-main .comparison-block{padding:2.8rem 0}
.article-main .comparison-block header{gap:2rem}
.article-main .comparison-block h3{font-size:clamp(1.5rem,2.8vw,2.6rem)}
.article-main .comparison-block header p{font-size:.94rem;line-height:1.7}
.article-main .comparison-summary{font-size:1.06rem;line-height:1.7;font-weight:600}
.article-main .comparison-wrap{margin-top:1.4rem}
.article-main .case-figure{margin:2rem 0 3rem}
.article-main .case-grid{margin:2rem 0 3rem}
.article-main .method-section .article-text{margin-bottom:1.5rem}
.article-main .chapter-mark{margin-bottom:2.5rem}
.article-main .article-chapter-lead{font-size:1.05rem;line-height:1.85}
@media(max-width:980px){.article-toc ol{grid-template-columns:repeat(2,minmax(0,1fr))}.article-toc li:nth-child(4n){border-right:1px solid var(--rule)}.article-toc li:nth-child(2n){border-right:0}}
@media(max-width:560px){.article-toc{padding:2.5rem 1.2rem}.article-toc ol{grid-template-columns:1fr}.article-toc li{border-right:0!important}.article-text{max-width:100%}.article-text p{font-size:1rem;line-height:1.85}.article-main .comparison-block header{grid-template-columns:1fr}}
"""
