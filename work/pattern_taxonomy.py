"""Orthogonal taxonomy facets for browsing the Agentic Pattern Atlas.

Taxonomy groups answer which architectural concern a pattern primarily serves.
They do not change the Common/Variant hierarchy or the separate treatment of
Compound Patterns in the complete atlas.
"""


TAXONOMY_GROUPS = {
    "application-responsibility": {
        "layer": "L1",
        "name_zh": "业务角色与责任边界",
        "name_en": "Application Responsibility",
        "description": "Agent 在业务工作中如何与人、流程和持续环境反馈建立责任关系。L1 条目数量较少，因此保持一个整体视角，不继续细分。",
        "patterns": (
            "embedded-copilot",
            "workflow-participant",
            "agentic-front-door",
            "autonomous-worker",
            "always-on-agent-worker",
            "continuous-controller",
        ),
    },
    "central-orchestration": {
        "layer": "L2",
        "name_zh": "中央调度与委派",
        "name_en": "Central Orchestration & Delegation",
        "description": "由一个明确的控制中心选择执行者、分解任务、管理生命周期或汇总结果。",
        "patterns": (
            "single-agent-system",
            "router-specialist",
            "supervisor-specialist",
            "inline-subagent",
            "agent-pool",
            "magentic-orchestration",
            "hierarchical-multi-agent",
        ),
    },
    "flow-responsibility-transfer": {
        "layer": "L2",
        "name_zh": "工作分发与责任转移",
        "name_en": "Work Distribution & Responsibility Transfer",
        "description": "通过 Workflow、并行分发或 Handoff 推进工作，重点是工作项怎样流动以及责任何时转移。",
        "patterns": (
            "workflow-centric-hybrid",
            "handoff",
            "sequential-agents",
            "parallel-agents",
            "fan-out-subagents",
        ),
    },
    "deliberation-consensus": {
        "layer": "L2",
        "name_zh": "多方讨论与共识",
        "name_en": "Deliberation & Consensus",
        "description": "多个 Agent 通过观点交换、批判、投票或共享对话形成结论。",
        "patterns": (
            "debate-consensus",
            "group-chat",
        ),
    },
    "decentralized-collaboration": {
        "layer": "L2",
        "name_zh": "去中心化与共享状态协作",
        "name_en": "Decentralized & Shared-State Collaboration",
        "description": "没有唯一中央控制者，协作依靠对等消息、事件、共享工作区或团队自治维持。",
        "patterns": (
            "peer-network",
            "event-choreography",
            "shared-blackboard",
            "autonomous-team",
        ),
    },
    "action-reasoning-loop": {
        "layer": "L3",
        "name_zh": "行动与推理循环",
        "name_en": "Action & Reasoning Loops",
        "description": "定义单个 Agent 如何感知、推理、规划并选择下一步行动。",
        "patterns": (
            "reactive-agent",
            "react-agent",
            "plan-and-execute",
            "bdi-agent",
        ),
    },
    "reflection-adaptation": {
        "layer": "L3",
        "name_zh": "评估、反思与学习",
        "name_en": "Evaluation, Reflection & Adaptation",
        "description": "通过评价、修订或经验更新改善当前输出与后续行为。",
        "patterns": (
            "reflection",
            "evaluator-optimizer",
            "learning-adaptation",
        ),
    },
    "goal-decision-policy": {
        "layer": "L3",
        "name_zh": "目标、资源与决策策略",
        "name_en": "Goals, Resources & Decision Policies",
        "description": "约束 Agent 如何设定目标、分配有限资源、排序工作与探索候选方案。",
        "patterns": (
            "goal-monitoring",
            "resource-aware",
            "reasoning-strategies",
            "exploration-discovery",
            "prioritization",
        ),
    },
    "workflow-composition": {
        "layer": "L3",
        "name_zh": "Workflow 组合结构",
        "name_en": "Workflow Composition",
        "description": "用顺序、分支与并行关系把模型调用和局部步骤组织成可复用控制结构。",
        "patterns": (
            "prompt-chaining",
            "routing",
            "parallelization",
        ),
    },
    "knowledge-grounding": {
        "layer": "L3",
        "name_zh": "知识检索与证据闭环",
        "name_en": "Knowledge Grounding",
        "description": "定义查询、检索、证据组装、生成和充分性判断之间的稳定协作结构。",
        "patterns": (
            "rag",
            "agentic-rag",
        ),
    },
    "action-control-boundaries": {
        "layer": "L3",
        "name_zh": "行动与控制边界",
        "name_en": "Action & Control Boundaries",
        "description": "定义 Agent 行动如何经过工具运行时、权限执行点或人工授权边界。",
        "patterns": (
            "tool-use",
            "human-in-loop",
            "agent-identity-policy",
        ),
    },
    "capability-discovery": {
        "layer": "L3",
        "name_zh": "能力发现",
        "name_en": "Capability Discovery",
        "description": "通过受治理的能力目录与解析关系，让调用方在运行时发现合适 Agent。",
        "patterns": (
            "agent-registry",
        ),
    },
    "reliable-execution": {
        "layer": "L3",
        "name_zh": "持久执行与一致性",
        "name_en": "Durable & Consistent Execution",
        "description": "通过检查点、恢复、局部事务与补偿关系，使长时和跨系统行动可靠推进。",
        "patterns": (
            "durable-agent-workflow",
            "saga-compensation",
        ),
    },
    "context-state-techniques": {
        "layer": "E",
        "name_zh": "上下文、记忆与提示技术",
        "name_en": "Context, Memory & Prompting Techniques",
        "description": "选择、保存、压缩并组织模型当前需要的信息和局部行为提示。",
        "patterns": (
            "memory-management",
            "context-engineering",
            "advanced-prompting",
        ),
    },
    "interoperability-formats": {
        "layer": "E",
        "name_zh": "互操作协议与能力格式",
        "name_en": "Interoperability Protocols & Capability Formats",
        "description": "标准化 Host、工具、资源、远程 Agent 与可复用能力包之间的连接契约。",
        "patterns": (
            "mcp",
            "a2a",
            "agent-skills",
        ),
    },
    "safety-operational-practices": {
        "layer": "E",
        "name_zh": "安全、恢复与运行实践",
        "name_en": "Safety, Recovery & Operational Practices",
        "description": "用防护、恢复策略、轨迹和评估实践约束并持续改善生产运行。",
        "patterns": (
            "exception-recovery",
            "guardrails",
            "evaluation-monitoring",
        ),
    },
}


def apply_pattern_taxonomy(patterns):
    pattern_ids = {pattern["id"] for pattern in patterns}
    assigned = {}
    for group_id, group in TAXONOMY_GROUPS.items():
        assert group["layer"] in {"L1", "L2", "L3", "E"}, f"Invalid catalog section for {group_id}"
        for pattern_id in group["patterns"]:
            assert pattern_id in pattern_ids, f"Unknown taxonomy pattern: {pattern_id}"
            assert pattern_id not in assigned, f"Pattern assigned to multiple taxonomy groups: {pattern_id}"
            assigned[pattern_id] = group_id

    missing = pattern_ids - set(assigned)
    assert not missing, f"Patterns without taxonomy group: {sorted(missing)}"

    by_id = {pattern["id"]: pattern for pattern in patterns}
    for pattern_id, group_id in assigned.items():
        group = TAXONOMY_GROUPS[group_id]
        assert by_id[pattern_id]["layer"] == group["layer"], f"Cross-layer taxonomy group: {pattern_id}"
        by_id[pattern_id]["taxonomy_group"] = group_id
        by_id[pattern_id]["taxonomy_name_zh"] = group["name_zh"]
        by_id[pattern_id]["taxonomy_name_en"] = group["name_en"]

    for pattern in patterns:
        if pattern["organization_role"] == "variant":
            parent = by_id[pattern["variant_of"]]
            assert pattern["taxonomy_group"] == parent["taxonomy_group"], (
                f"Common and Variant must share taxonomy group: {pattern['id']}"
            )
