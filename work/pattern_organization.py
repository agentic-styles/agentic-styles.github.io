"""Curated organization relationships for the public atlas.

Only atomic specializations appear as parent/child common + variant relations.
Compound patterns remain flat and may link to patterns that help explain their
composition; those links never imply a single-parent hierarchy.
"""

COMMON_VARIANTS = {
    "autonomous-worker": (
        "always-on-agent-worker",
    ),
    "supervisor-specialist": (
        "inline-subagent",
        "agent-pool",
    ),
    "parallel-agents": (
        "fan-out-subagents",
    ),
    "reflection": (
        "evaluator-optimizer",
    ),
    "reasoning-strategies": (
        "exploration-discovery",
    ),
    "rag": (
        "agentic-rag",
    ),
}


COMPOUND_PATTERNS = {
    "workflow-centric-hybrid": {
        "composed_of": ("workflow-participant", "human-in-loop"),
        "note": "将确定性 Workflow、受限 Agent 活动与可选人工门禁组合为端到端系统。",
    },
    "sequential-agents": {
        "composed_of": ("handoff", "workflow-centric-hybrid"),
        "note": "具体实例可以是重复 Handoff 的责任转移链，也可以是 Workflow 持有控制权的 Agent Pipeline。",
    },
    "magentic-orchestration": {
        "composed_of": ("supervisor-specialist", "shared-blackboard", "plan-and-execute", "goal-monitoring"),
        "note": "把中央协调、共享任务账本、运行时规划与进度监控组合成可持续修订的编排。",
    },
    "hierarchical-multi-agent": {
        "composed_of": ("supervisor-specialist",),
        "note": "递归应用 Supervisor-Specialist，在多个层级分解目标并汇总结果。",
    },
    "durable-agent-workflow": {
        "composed_of": ("workflow-centric-hybrid", "exception-recovery", "memory-management"),
        "note": "将 Agent Workflow、恢复路径与持久状态组合为可跨中断继续的长期运行。",
    },
    "saga-compensation": {
        "composed_of": ("sequential-agents", "exception-recovery"),
        "note": "将顺序业务动作、失败分类与反向补偿组合成跨系统一致性恢复方案。",
    },
}


def apply_pattern_organization(patterns):
    ids = {pattern["id"] for pattern in patterns}
    variant_parent = {}
    for common_id, variant_ids in COMMON_VARIANTS.items():
        assert common_id in ids, f"Unknown common pattern: {common_id}"
        for variant_id in variant_ids:
            assert variant_id in ids, f"Unknown variant pattern: {variant_id}"
            assert variant_id not in variant_parent, f"Variant has multiple parents: {variant_id}"
            variant_parent[variant_id] = common_id

    compound_ids = set(COMPOUND_PATTERNS)
    assert compound_ids <= ids, f"Unknown compound patterns: {sorted(compound_ids - ids)}"
    assert not compound_ids & set(COMMON_VARIANTS), "A common pattern cannot also be compound"
    assert not compound_ids & set(variant_parent), "A variant cannot also be compound"

    by_id = {pattern["id"]: pattern for pattern in patterns}
    for compound_id, definition in COMPOUND_PATTERNS.items():
        unknown = set(definition["composed_of"]) - ids
        assert not unknown, f"Unknown components for {compound_id}: {sorted(unknown)}"

    for pattern in patterns:
        pattern_id = pattern["id"]
        if pattern_id in COMMON_VARIANTS:
            pattern["organization_role"] = "common"
            pattern["variants"] = list(COMMON_VARIANTS[pattern_id])
            pattern["variant_of"] = None
            pattern["composed_of"] = []
            pattern["composition_note"] = None
        elif pattern_id in variant_parent:
            pattern["organization_role"] = "variant"
            pattern["variants"] = []
            pattern["variant_of"] = variant_parent[pattern_id]
            pattern["composed_of"] = []
            pattern["composition_note"] = None
        elif pattern_id in COMPOUND_PATTERNS:
            definition = COMPOUND_PATTERNS[pattern_id]
            pattern["organization_role"] = "compound"
            pattern["variants"] = []
            pattern["variant_of"] = None
            pattern["composed_of"] = list(definition["composed_of"])
            pattern["composition_note"] = definition["note"]
        else:
            pattern["organization_role"] = "standalone"
            pattern["variants"] = []
            pattern["variant_of"] = None
            pattern["composed_of"] = []
            pattern["composition_note"] = None

    for common_id, variant_ids in COMMON_VARIANTS.items():
        common_layer = by_id[common_id]["layer"]
        assert all(by_id[variant_id]["layer"] == common_layer for variant_id in variant_ids), (
            f"Common and variants must remain in one level: {common_id}"
        )


def organized_layer_patterns(patterns, layer):
    """Return one-level parent/child order, with compounds at the end."""
    layer_patterns = [pattern for pattern in patterns if pattern["layer"] == layer]
    by_id = {pattern["id"]: pattern for pattern in layer_patterns}
    variants = {variant for children in COMMON_VARIANTS.values() for variant in children}
    compounds = [pattern for pattern in layer_patterns if pattern["organization_role"] == "compound"]
    ordered = []
    for pattern in layer_patterns:
        pattern_id = pattern["id"]
        if pattern_id in variants or pattern["organization_role"] == "compound":
            continue
        ordered.append(pattern)
        ordered.extend(by_id[variant_id] for variant_id in COMMON_VARIANTS.get(pattern_id, ()))
    ordered.extend(compounds)
    assert len(ordered) == len(layer_patterns)
    assert len({pattern["id"] for pattern in ordered}) == len(layer_patterns)
    return ordered
