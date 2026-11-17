# Agentic Pattern Field Course｜逐页口语化演讲稿

> 对应 `presentation.html` 当前 64 页版本。建议总时长约 90 分钟，包含互动、停顿和简短答疑。正文不要求逐字照读，可把加粗句作为每页必须讲清的落点。

## 开场与分类框架｜约 14 分钟

### Slide 01｜标题（约 1 分钟）

大家好，今天这 90 分钟，我们不打算把几十个 Agent Pattern 逐条背一遍。我们要解决的是一个更实际的问题：当大家看到 ReAct、RAG、Multi-Agent、MCP 这些词时，怎样判断它们是不是在回答同一个架构问题？

今天的方法很简单：**先分层，再看结构，最后讨论组合。**课程主要讲稳定的 Common Pattern；Variant 只在相关 Common 后面顺带解释；真正由多个结构组成的 Compound Pattern，我们会单独拆解。

### Slide 02｜错误的四选一（约 1.5 分钟）

先做一个快速投票。假设我们要建设企业异常诊断助手，大家觉得应该选 ReAct、Multi-Agent、RAG，还是 MCP？先不要分析太久，在聊天区打出你的第一反应。

我给大家十秒钟。这里没有要考大家某个框架的 API，我只是想看看：当这些术语并列出现时，我们会不会本能地把它们当成互斥选项。

### Slide 03｜它们回答不同问题（约 1.5 分钟）

答案是：这道四选一从一开始就问错了。一个真实系统完全可能四个都用。

ReAct 回答的是一个 Agent 怎样根据反馈决定下一步；Multi-Agent 回答多个自治单元怎样组织；RAG 回答知识怎样进入上下文；MCP 回答 Host 怎样连接外部能力。

所以看到两个名词时，第一步不是比较优劣，而是先问：**它们的 System of Interest 是不是同一个？**

### Slide 04｜学习目标（约 1 分钟）

今天结束时，我希望大家形成三个动作。第一，先归层：它在改变业务责任、系统组织、Agent 内部设计，还是仅仅提供实现手段？第二，再辨结构：谁持有目标，谁决定下一步，状态在哪里？第三，才看关系：它是独立结构、Common 的有限变化，还是几个结构的复合。

如果能把这三个问题问顺，大家以后看到新的框架名词，也不会立刻被它的命名带走。

### Slide 05｜什么是 Architecture Pattern（约 1.5 分钟）

我们先统一 Pattern 的含义。Architecture Pattern 不是一段 prompt，也不是某个 SDK 的类名。它描述的是一种可重复的系统组织方式：有哪些参与者，它们之间怎样协作，谁持有责任和控制权。

最实用的判断方法是：换掉这个 Pattern 之后，目标所有者、决策权、自治边界或者状态关系会不会改变？如果会，它大概率在架构层面；如果只是换了调用格式或模型供应商，通常不是。

### Slide 06｜分类边界（约 1.5 分钟）

这一页是整门课的分类边界。Application Pattern 讨论人、流程与 Agent 的业务责任；Architecture Pattern 讨论系统中的控制权和组织方式；Design Pattern 讨论 Agent 与局部控制结构；Enablers 则是跨层支撑它们的技术、协议和实践。

这里最容易犯的错误，是把所有带图的东西都叫 Architecture Pattern。**重要不等于处于同一层。**MCP 很重要，评估也很重要，但它们不会自动决定谁拥有业务目标。

### Slide 07｜相似的图不代表相同层级（约 1.5 分钟）

这三张图看起来都是从左到右的箭头，但语义完全不同。Prompt Chaining 是固定的调用链；Sequential Agents 的每个阶段拥有独立角色和局部自治；Handoff 更进一步，它转移了后续会话责任。

所以不要只数方框和箭头。要看节点有没有自己的局部目标、状态、决策循环和停止条件。**拓扑相似，不代表责任结构相同。**

### Slide 08｜三层地图（约 1 分钟）

现在把地图拉开。L1 把完整业务应用当作 System of Interest；L2 把 Agentic System 当作完整系统；L3 再进入单个 Agent 和局部设计结构。Enablers 不作为第四层，而是可以支撑多个层级的实现手段。

后面每遇到一个 Pattern，我们都先在这张地图上定位，再讨论细节。

### Slide 09｜两个组织轴（约 1 分钟）

图鉴用两个轴组织内容。纵轴回答 Pattern 在哪里生效，也就是 L1、L2、L3 和 Enablers。横轴回答 Pattern 之间是什么关系：Standalone、Common、Variant，还是 Compound。

这两个轴不要混在一起。层级是在说“研究对象”，关系是在说“条目之间怎样继承或组合”。

### Slide 10｜Common 与 Variant（约 1 分钟）

课程里我们会淡化 Variant，因为先掌握 Common 才有价值。Common 保存稳定的参与者、责任和控制关系；Variant 只是在这个核心上增加一个明确限定。

例如 Supervisor 仍然持有总体目标，只是 Specialist 可能是一次性的，也可能是持久的。核心责任没变，所以它们可以作为 Variant 顺带理解。

### Slide 11｜Compound Pattern（约 1.5 分钟）

Compound 不一样。它不是在 Common 上改一个参数，而是把多个基础结构组合、重复，甚至递归使用。

Sequential Agents 需要阶段化 Agent、控制与状态交接；Hierarchical Multi-Agent 是 Supervisor 的递归；Magentic 还会组合任务账本、规划和目标监控。**看到 Compound，要问它由什么组成，而不是问它是谁的 Variant。**

## L1：业务责任中的 Agent｜约 10 分钟

### Slide 12｜L1 章节（约 45 秒）

进入 L1。这里先不管系统内部有几个 Agent，而是从业务责任看：人在不在执行过程中？Agent 是辅助一个活动，还是代表用户推进整个任务？

接下来四个 Pattern 彼此独立，不是 Common 和 Variant，所以我们逐个讲。

### Slide 13｜Workflow Participant 案例（约 1.5 分钟）

第一个是 Agentic Workflow Participant。以费用报销为例，材料解释可以交给 Agent，但经理审批、预算检查、合规批准的顺序不能由 Agent 随意改变。

工作流拥有端到端状态，也知道什么时候暂停等人、什么时候恢复。Agent 只是其中一个概率性节点。判断关键是：**如果拿掉这个 Agent，业务流程仍然存在，只是其中一步换回人工或规则实现。**

### Slide 14｜Embedded Copilot 案例（约 1.5 分钟）

Embedded Copilot 的典型案例是 GitHub Copilot。开发者始终在 IDE 里工作，Copilot 根据当前代码和上下文提供候选修改，但人持续审阅差异、运行测试，并决定是否提交。

它的价值是增强人的工作台，而不是接管任务。只要用户必须持续在场，而且最终行动仍由用户确认，这就更接近 Copilot，而不是后台 Autonomous Worker。

### Slide 15｜Agentic Front Door 案例（约 1.5 分钟）

Agentic Front Door 是统一的任务入口。比如员工不需要知道密码重置属于 IT、假期余额属于 HR、采购申请属于哪个系统，只需要面对一个入口。

入口 Agent 代表用户做跨域导航和结果整合。注意，这只是 L1 的业务形态。往下实现时仍然要决定是 Router、Supervisor 还是 Handoff，Front Door 本身不会替我们回答这些 L2 问题。

### Slide 16｜Autonomous Worker 案例（约 1.5 分钟）

Autonomous Worker 的特点是人给出目标后，不需要逐步在场。以 OpenHands 为例，开发者交给它一个边界明确的软件工程任务，它可以在受控环境中查看仓库、修改代码、运行验证，最后把结果和证据交回来。

“自主”不代表没有人负责。目标边界、异常升级和最终合并仍属于工程团队。它只是把执行过程从同步协作变成异步委托。

### Slide 17｜L1 四象限互动（约 2 分钟）

现在请大家把四个 Pattern 放进象限。横轴是人与执行过程的耦合程度，纵轴是 Agent 推进任务的自主度。A、B、C、D 分别应该放谁？

请先给出位置，再补一句依据。不要用“看起来更智能”作为依据，要用人在不在场、谁推进任务、谁拥有最终责任来解释。给大家 40 秒，然后请两位同学分享。

### Slide 18｜L1 四象限答案（约 1.25 分钟）

对照答案看，Workflow Participant 的自主范围窄，并且被流程紧密约束；Embedded Copilot 需要人持续在场；Front Door 代表用户跨域协调，但通常仍保持交互；Autonomous Worker 则在委托后自主推进。

这张图是定性地图，不是成熟度排名。选择越靠右上并不代表越先进，只代表更高自治，也意味着更高的治理和恢复成本。

## L2：Agentic System 的组织结构｜约 25 分钟

### Slide 19｜L2 章节（约 45 秒）

进入 L2，我们才真正讨论一个还是多个 Agent。这里的三个关键词是目标所有权、控制权和共享状态。

请暂时忘掉框架的营销名称，只问：谁决定下一步？结果返回给谁？会话责任有没有转移？

### Slide 20｜Single Agent 案例（约 1.5 分钟）

Single-Agent System 应该是默认基线，而不是“初级方案”。SWE-agent 可以用一个 Agent 反复搜索、编辑和测试，所有观察和决策保留在同一条轨迹里。

如果工具、权限和上下文都能安全放在一个边界中，就没有必要为了角色名称拆成多个 Agent。**先证明一个 Agent 不够，再承担多 Agent 的协调成本。**

### Slide 21｜Supervisor 案例（约 1.75 分钟）

Supervisor-Specialist 是最常见的 Common Pattern。研究任务中，中央 Agent 选择研究、数学或写作专家，专家完成局部任务后把结果交回，中央 Agent 再决定下一步并完成综合。

它不是一次性 Router，因为协调会持续多个回合。关键不在有没有一个叫 supervisor 的组件，而在总体目标、分派权和最终答案是不是一直留在中央协调者。

### Slide 22｜Supervisor Variants（约 1.25 分钟）

这里顺带看两个 Variant。Inline Tool Subagent 是一次性、隔离上下文的专家调用，完成后只返回结果；Agent Pool 则保留持久专家身份，可以在长任务里反复追加工作。

生命周期不同，但总体目标、分派权和综合责任都没有离开 Supervisor，所以它们属于同一个核心结构的变化。

### Slide 23｜Router、Supervisor、Handoff（约 2 分钟）

这三者经常被混用，但它们不是彼此的轻量 Variant。Router 选择一次去向，处理完成后返回原调用方；Supervisor 持续中央协调；Handoff 则把后续会话责任交给目标 Agent。

最有效的判断问题只有一句：**箭头之后，谁拥有下一步？**如果答案仍然是入口，就是 Router；持续回到中央，是 Supervisor；目标 Agent 接管，就是 Handoff。

### Slide 24｜Parallel Agents 案例（约 1.5 分钟）

Parallel Agents 并行的不是几次 API 调用，而是自治单元。事故调查中，日志、数据库和网络三个分析 Agent 可以同时工作，各自拥有局部目标、工具循环和停止条件，最后再聚合结果。

如果只是把三个 prompt 并发执行，没有各自的决策循环，那只是 L3 的 Parallelization，不必称为并行多 Agent。

### Slide 25｜Fan-Out Variant（约 1.25 分钟）

Fan-Out Subagents 是 Parallel Agents 的一个清晰 Variant：成员不是设计时长期存在，而是为当前任务临时 Spawn，统一 Wait，完成后 End。

它适合可拆分、边界清楚、生命周期短的研究或分析任务。代价是每个子 Agent 都有启动、上下文复制和结果整合成本，所以扇出数量不是越多越好。

### Slide 26｜Group Chat 案例（约 1.5 分钟）

Group Chat 的核心是所有参与者共享同一条累积会话。比如产品、工程和审校轮流完善一个方案，每个人都需要看到之前说过什么，再决定自己的贡献。

AutoGen 的 RoundRobin 或 Selector 负责选择下一位发言者。它与 Supervisor 的区别是，中间讨论本身是共享媒介，而不是专家只把局部结果交给中央协调者。

### Slide 27｜共享协作相关模式（约 1.5 分钟）

共享什么，会产生不同协作语义。Group Chat 共享完整讨论；Debate & Consensus 共享主张、反驳和裁决过程；Shared Blackboard 共享问题状态与中间产物。

共同点是中间状态会被其他参与者读取和继续修改。选择时要问：我们真的需要共享全过程，还是只需要收回最终结果？共享越多，耦合和上下文成本越高。

### Slide 28｜Peer Network 案例（约 1.5 分钟）

Peer Agent Network 没有持续中央协调者。AutoGen Swarm 的客服、销售和售后可以根据当前会话直接 Handoff 给下一个合适角色，不必每次绕回 Supervisor。

优点是减少中央瓶颈，领域节点可以直接协作；代价是责任轨迹更难看清。因此必须有明确的交接协议、允许的下一跳和终止条件。

### Slide 29｜去中心化相关模式（约 1.5 分钟）

去中心化也有不同推进媒介。Peer Network 由当前节点选择下一跳；Event Choreography 依靠事件和订阅异步推进；Autonomous Team 则由稳定成员共同拥有团队内部协调。

它们不是单纯“去掉 Supervisor”这么简单。中央协调消失以后，冲突处理、共享状态一致性和最终业务责任都要在别处得到解决。

### Slide 30｜Workflow-Centric Hybrid（约 1.5 分钟）

第一个 Compound 是 Workflow-Centric Hybrid。以 LangGraph 为例，固定门禁、重试、人工审批和结束条件由确定性 Workflow 管理；Agent 只在资料解释等局部步骤中自主推理。

它的价值是把概率性能力放进确定性外壳。对合规、财务或长流程系统，这通常比让一个 Agent 拥有全部流程控制权更容易审计和恢复。

### Slide 31｜Sequential Agents（约 1.5 分钟）

Sequential Agents 看起来像 Prompt Chaining，但每个阶段是有身份、有局部目标和停止条件的 Agent。比如研究、写作、审校三个角色依次产生产物并交接。

所以“顺序”只是表面。真正让它升级为 L2 Compound 的，是阶段化 Agent 身份，加上 Handoff 或 Workflow Control，再加状态化的产物交接。

### Slide 32｜Hierarchical Multi-Agent（约 1.5 分钟）

Hierarchical Multi-Agent 是 Supervisor 结构的递归。上层 Manager 分解目标，中层可能继续管理自己的专家，结果再逐层汇总。

它适合规模和权限确实存在层级的任务，但层级越深，信息损失、延迟和责任模糊越明显。不要因为组织图有三层，就自动让 Agent 系统也复制三层。

### Slide 33｜Magentic Orchestration（约 1.75 分钟）

Magentic Orchestration 面向步骤无法预先列全的开放任务。它不只是 Supervisor 调专家，还显式维护任务账本：计划是什么、完成了什么、卡在哪里、是否需要重规划。

当新证据推翻原计划时，管理者更新账本并重新分派。它是 Supervisor、Shared Blackboard、Plan-and-Execute 和 Goal Monitoring 的组合，所以是 Compound，而不是 Supervisor 的轻量 Variant。

### Slide 34｜L2 配方互动（约 1.5 分钟）

现在看这份配方：中央协调者、共享任务账本、运行时规划、持续进度修订。它最接近哪个 Compound Pattern？

请大家不只说“Magentic”，还要解释为什么不只是 Supervisor。收束答案是：因为任务账本、显式计划和进度监控都成为一等结构，计划本身也会在运行时被修订。

### Slide 35｜认知复位（约 1 分钟）

我们做一次聊天瀑布。请大家输入目前最容易混淆的一对 Pattern，但先不要发送。可以是 Router 和 Handoff，也可以是 Parallel Agents 和 Parallelization。

三、二、一，一起发送。快速看一下高频答案。后面听 L3 时，请大家带着自己写下的这对概念，观察它们到底跨没跨层。

## L3：Agent 与局部设计结构｜约 23.5 分钟

### Slide 36｜L3 章节（约 45 秒）

进入 L3，我们把 System of Interest 缩小到 Agent 和局部控制结构。这里既有认知循环，也有 Workflow、检索、行动和可靠执行结构。

判断标准仍然是：它是否表达稳定的参与者、关系、控制流和后果，而不只是某个实现技巧。

### Slide 37｜ReAct 案例（约 1.5 分钟）

ReAct 是推理、行动、观察的循环。修复代码缺陷时，Agent 一开始不知道要查看哪些文件；它先搜索或运行测试，再依据最新结果决定下一步。

重点不在输出里有没有写出 Thought，而在控制流是否真的依赖环境反馈。如果下一步早已固定，那就是 Workflow；如果每次观察都会改变后续行动，才是 ReAct 式控制。

### Slide 38｜相关控制循环（约 1.75 分钟）

这四个结构的区别在规划深度。Reactive 根据当前信号直接行动；ReAct 在每轮反馈后决定下一步；Plan-and-Execute 先形成全局计划，再执行和重规划；BDI 进一步显式管理信念、愿望与意图承诺。

这些都可以发生在一个 Agent 内部。内部有多个阶段、多个候选，不等于系统里已经出现多个 L2 Agent。

### Slide 39｜Reflection 案例（约 1.5 分钟）

Reflection 用反馈推动再次生成。AutoGen 的示例中，Primary 产生初稿，Critic 检查遗漏和表达，Primary 根据意见继续修改，直到满足通过条件。

适用前提是任务可以通过反馈逐步改善。如果没有评价标准、反馈无法指导修改，循环只会增加 token，而不会稳定提高质量。

### Slide 40｜Evaluator–Optimizer Variant（约 1.25 分钟）

Evaluator–Optimizer 把 Reflection 里的评价权显式分离。生成者负责候选，评价者按清晰标准给反馈，并判断是否结束。

这里要注意跨层：逻辑上有生成和评价两个角色，不代表部署上必须是两个 Agent。它可以是一个 Agent 内的两个步骤；是否拆成 L2 多 Agent，要看权限、状态和自治边界。

### Slide 41｜Goal Monitoring 案例（约 1.5 分钟）

开放任务很容易重复搜索、遗漏子目标或困在失败路径。Goal Setting and Monitoring 把目标、完成项和阻塞显式保存，让“进度”本身成为可读取的状态。

Magentic-One 的任务账本就是例子。它不仅记录日志，还要回答：我们离目标还有多远？是否偏离？是否停滞？什么时候算完成？

### Slide 42｜相关运行策略（约 1.5 分钟）

这三种策略管理的对象不同。Prioritization 管工作顺序；Resource-Aware 管模型、工具和预算；Learning & Adaptation 管跨任务的行为变化。

它们都能改变 Agent 的运行政策，但不会自动改变 L2 责任边界。比如把昂贵模型换成便宜模型，是资源策略变化，不会让 Single Agent 突然变成 Multi-Agent。

### Slide 43｜Reasoning Strategies 案例（约 1.5 分钟）

Reasoning Strategies 组织一个 Agent 内部的候选搜索路径。DSPy 可以把 ReAct 等模块组合成可评估的程序，并根据指标优化，而不是对所有任务固定使用同一种思维链。

请记住：一个模型生成五条候选路径再投票，仍然可能只是一个 Agent 的内部搜索。候选数量不是 Agent 数量。

### Slide 44｜Exploration Variant（约 1.25 分钟）

Exploration & Discovery 把搜索空间进一步打开。普通 Reasoning Strategies 在候选路径中推理和选择；探索模式还会主动提出未知假设、寻找新证据、保存结果并剪枝。

新增的代价是成本更高，而且可能不收敛。因此预算、证据质量和停止条件必须成为设计的一部分。

### Slide 45｜L3 判断互动（约 1.5 分钟）

问题来了：一个模型生成五条推理路径，再用自洽投票选答案，这是 Parallel Agents，还是一个 Agent 内部的 Reasoning Strategy？

答案通常是后者，因为没有五个独立的目标所有者、工具循环和停止条件。除非这五条路径由真正隔离且自治的 Agent 分别推进，否则不要因为“并行”就把它归到 L2。

### Slide 46｜L3 设计结构续（约 45 秒）

接下来继续 L3，但从认知循环转向局部 Workflow、行动、检索和可靠执行。它们仍然是 Design Pattern，因为会稳定地组织参与者、控制流、状态和失败后果。

而协议、格式和工程实践会在稍后的 Enablers 单独讨论。

### Slide 47｜Prompt Chaining 案例（约 1.5 分钟）

Prompt Chaining 适合步骤在设计时已经明确的任务。比如营销文案先提取产品事实，再生成草稿，最后按照品牌规则检查；步骤之间还可以加入确定性门禁。

这里每个节点只是模型或工具调用，没有独立 Agent 身份和自治循环。固定流程能解决，就不要先升级成 Sequential Agents。

### Slide 48｜相关局部流程（约 1.5 分钟）

局部控制流可以有四种常见变化：固定顺序用 Prompt Chaining；先分类再分支用 Routing；同时执行后聚合用 Parallelization；只改变单次调用推理方式，则属于 Advanced Prompting。

这些结构都可以存在于一个 Agent 或一个 Workflow 内部。它们改变调用方式，但不必改变系统责任架构。

### Slide 49｜Tool Use 案例（约 1.5 分钟）

模型本身不能查看真实文件、编辑代码或运行测试，Tool Use 给 Agent 提供行动接口。SWE-agent 把 Bash、文件查看和编辑能力组织成受控工具，Agent 执行动作，再根据结果继续决策。

工具不是新的 Agent。真正要设计的是权限、参数校验、副作用、幂等、超时和失败恢复，而不只是函数 schema。

### Slide 50｜相关能力与状态机制（约 1.5 分钟）

行动之外，还要回答 Agent 带着什么去行动。Context Engineering 选择和压缩当前信息；Memory Management 保存跨步骤或跨会话状态；Agent Skills 封装可复用的方法、说明和脚本。

Tool 提供“能做什么”，Context、Memory 和 Skills 决定“带着什么信息、经验和方法去做”。它们互补，但不要把每一种能力都包装成新 Agent。

### Slide 51｜RAG 案例（约 1.5 分钟）

RAG 把模型参数之外的证据带进当前上下文。以 LlamaIndex 为例，企业私有文档先被解析和索引，请求到来时检索相关片段，再让模型基于证据回答。

如果数据源、触发方式和检索次数都可以预先配置，一次检索就够，就保持普通 RAG。简单结构通常更低延迟，也更容易评估。

### Slide 52｜Agentic RAG Variant（约 1.25 分钟）

当检索本身需要运行时决策，就进入 Agentic RAG：Agent 判断要不要检索、怎样改写查询、选择哪个数据源，以及证据是否足够，必要时继续下一轮。

它保留了 RAG 的核心目标，但增加闭环控制。收益是处理复杂信息需求，代价是循环、延迟、成本和错误证据传播风险同步上升。

## Enablers 与可靠执行｜约 11 分钟

### Slide 53｜Enablers 章节（约 45 秒）

现在把 Pattern 和实现手段分开。Enablers 包括技术、协议和工程实践，它们可以跨 L1、L2、L3 复用或替换，所以不构成第四层 Pattern。

它们回答的是怎样连接、怎样保存、怎样限制、怎样观察，而不是谁拥有业务目标。

### Slide 54｜MCP 案例（约 1.5 分钟）

MCP 统一了 Host 连接 Tools、Resources 和 Prompts 的方式。官方参考 Servers 展示了 Filesystem、Git、Memory 等能力如何用同一协议暴露。

但 Host Agent 仍然拥有任务。接入十个 MCP Server 也不会自动产生十个 Agent，更不会替我们决定是 Router、Supervisor 还是 Handoff。

### Slide 55｜相关互操作机制（约 1.5 分钟）

MCP、A2A 和 Agent Registry 的连接对象不同。MCP 是 Host 对工具或资源服务；A2A 是 Agent 对远程 Agent，能够委派长任务并接收状态和产物；Registry 用于连接前发现能力和协议元数据。

它们定义契约，但不定义上层组织。协议解决“怎么说话”，Pattern 解决“谁对什么负责”。

### Slide 56｜Guardrails 案例（约 1.5 分钟）

Guardrails 要把安全规则放在模型的概率性判断之外。NeMo Guardrails 可以在输入、对话、检索、执行和输出等边界运行可编程 Rails。

不要只在 system prompt 里写“请勿执行危险操作”。真正的控制需要落在可执行边界：检查输入、限制工具权限、验证参数、拦截输出，并留下审计证据。

### Slide 57｜相关控制机制（约 1.5 分钟）

完整治理面至少回答四个问题：Identity & Policy 决定谁有权行动；Human-in-the-Loop 决定何时交回人类；Exception Recovery 决定失败后重试、回退、升级还是终止；Evaluation & Monitoring 提供质量和运行证据。

原则很简单：**自治越高，停止、权限、恢复和观测越要确定。**

### Slide 58｜Durable Agent Workflow（约 1.5 分钟）

Durable Agent Workflow 是可靠执行的 Compound。长达数日的审批流程会经历缩容、部署、故障和人工等待，因此运行状态不能绑在某个进程上。

它组合 Workflow-Centric Hybrid、Exception Recovery 和 Memory 或 Checkpoint。恢复后要从正确位置继续，而且已经完成的副作用不能重复执行。

### Slide 59｜Saga 与补偿动作（约 1.5 分钟）

跨系统业务操作通常没有一个全局事务。旅行预订里，车辆、酒店和机票各自局部提交；如果后续失败，就按照逆序执行预先登记的 Compensation。

Saga 不是简单重试。重试是再次尝试同一个动作；补偿是执行一个业务上抵消前序效果的新动作，而且必须可追踪。

### Slide 60｜Enabler 判断互动（约 1.5 分钟）

最后一个判断题：一次工具调用失败后自动重试三次，它是什么？答案是 Exception Recovery 的局部策略。

它不是 Saga，因为没有跨系统业务动作和逆序补偿；也不是 Durable Agent Workflow，因为没有持久状态、Checkpoint、长时等待和恢复语义。请大家说说，要升级到后两者还缺什么结构。

## 综合案例与收束｜约 6.5 分钟

### Slide 61｜三层组合案例（约 1.5 分钟）

现在把地图重新合起来。一个真实系统不会只选一个 Pattern：L1 决定人和 Agent 的业务关系；L2 决定 Agent 如何组织；L3 决定内部怎样推理、调用和检索；Enablers 再提供连接、安全、记忆和评估能力。

关键是组合前先归层。这样每个选择都有明确理由，也知道它增加了什么成本。

### Slide 62｜案例复盘（约 1.75 分钟）

回到企业异常诊断助手。L1 可以采用 Copilot，让业务人员保留最终责任；L2 用 Workflow 包住确定性门禁，再用 Supervisor 协调诊断专家；L3 使用 ReAct、规划、RAG 和高风险 HITL；Enablers 再补 Context、MCP、Trace 和 Evals。

所以开场的四个选项并不冲突，它们分别落在组合中的不同位置。

### Slide 63｜四个决策问题（约 1.75 分钟）

以后选 Pattern，可以从四个问题开始。第一，谁拥有最终目标和失败责任？第二，谁决定下一步，控制权有没有转移？第三，哪些状态共享，哪些上下文隔离？第四，如果不用更高自治结构，具体会损失什么？

第四问尤其重要。如果说不出明确收益，就保留更小、更容易解释和恢复的结构。

### Slide 64｜总结（约 1.5 分钟）

今天最重要的不是记住多少名字，而是形成顺序：先问层级，再看责任和控制结构，最后才谈变体与组合。

请大家离开前在聊天区留下三个答案：一个你现在能正确归层的 Pattern；一个你能解释的 Common–Variant 关系；一个你不会再误判为 Variant 的 Compound Pattern。

最后送大家一句选择原则：**选择满足目标的最小自治、最小协调结构。**谢谢大家，接下来我们留一点时间处理最集中的问题。

---

## 讲师时间控制提示

- 开场与分类框架：约 14 分钟
- L1：约 10 分钟
- L2：约 24.75 分钟
- L3：约 23.5 分钟
- Enablers：约 11.25 分钟
- 综合与收束：约 6.5 分钟
- 页面标注合计约 90 分钟；如希望预留集中问答，可从案例页各压缩 10–15 秒，腾出约 5 分钟机动时间。
