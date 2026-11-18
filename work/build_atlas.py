from __future__ import annotations

import csv
import copy
import html
import io
import json
import os
import re
from pathlib import Path

from atlas_data import ACCESSED_AT, CHAPTERS, ENABLER_META, LAYER_META, PATTERNS, PDF_PATH, SOURCES
from blog_content import (
    ANCHOR_IDS,
    BLOG,
    CASE_STEPS,
    COMPARISONS,
    DECISION_QUESTIONS,
    READING_PATHS,
    SELECTED_SOURCE_IDS,
)
from pattern_organization import organized_layer_patterns
from pattern_taxonomy import TAXONOMY_GROUPS


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"
OUTPUT = Path(os.environ.get("ATLAS_OUTPUT_DIR", ROOT / "dist" / "atlas")).resolve()
DIAGRAMS = OUTPUT / "diagrams"
ASSETS = OUTPUT / "assets"
DATA = OUTPUT / "data"

BLOG["author"] = os.environ.get("ATLAS_AUTHOR", BLOG["author"])
BLOG["author_type"] = os.environ.get("ATLAS_AUTHOR_TYPE", "Organization")


PALETTE = {
    "paper": "#F4F0E7",
    "paper2": "#FBF8F1",
    "ink": "#172331",
    "muted": "#5A6671",
    "line": "#9BA5AC",
    "agent": "#DCE8F6",
    "agent_stroke": "#315EA8",
    "human": "#F5D8CE",
    "human_stroke": "#B5472D",
    "workflow": "#D8ECE8",
    "workflow_stroke": "#1C6E67",
    "tool": "#F1E6BD",
    "tool_stroke": "#896B24",
    "memory": "#E8DFF0",
    "memory_stroke": "#73558A",
    "policy": "#F5DDD4",
    "policy_stroke": "#9A3D31",
    "external": "#E7E9E8",
    "external_stroke": "#5A6671",
}


def esc(value):
    return html.escape(str(value), quote=True)


def bilingual_name(pattern, *, block=False):
    """Render an English-first Pattern name with a subdued Chinese translation."""
    tag = "span" if block else "small"
    return (
        f'<span class="term-en" lang="en">{esc(pattern["name_en"])}</span>'
        f'<{tag} class="term-zh" lang="zh-Hans">{esc(pattern["name_zh"])}</{tag}>'
    )


def bilingual_taxonomy_name(group, *, block=False):
    tag = "span" if block else "small"
    return (
        f'<span class="term-en" lang="en">{esc(group["name_en"])}</span>'
        f'<{tag} class="term-zh" lang="zh-Hans">{esc(group["name_zh"])}</{tag}>'
    )


def lines(text, max_chars=15):
    words = str(text).split()
    if len(words) > 1:
        result, current = [], ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if len(candidate) > max_chars and current:
                result.append(current)
                current = word
            else:
                current = candidate
        if current:
            result.append(current)
        return result[:3]
    text = str(text)
    if len(text) <= max_chars:
        return [text]
    return [text[i:i + max_chars] for i in range(0, len(text), max_chars)][:3]


def multiline(x, y, label, size=22, color=None, weight=650, anchor="middle", gap=None):
    color = color or PALETTE["ink"]
    gap = gap or int(size * 1.28)
    chunks = lines(label, 17 if size >= 22 else 21)
    start = y - ((len(chunks) - 1) * gap) / 2
    tspans = "".join(
        f'<tspan x="{x}" y="{start + i * gap:.0f}">{esc(chunk)}</tspan>'
        for i, chunk in enumerate(chunks)
    )
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{color}">{tspans}</text>'


def node(x, y, w, h, label, role="agent", subtitle=None):
    fills = {
        "agent": (PALETTE["agent"], PALETTE["agent_stroke"]),
        "human": (PALETTE["human"], PALETTE["human_stroke"]),
        "workflow": (PALETTE["workflow"], PALETTE["workflow_stroke"]),
        "tool": (PALETTE["tool"], PALETTE["tool_stroke"]),
        "memory": (PALETTE["memory"], PALETTE["memory_stroke"]),
        "policy": (PALETTE["policy"], PALETTE["policy_stroke"]),
        "external": (PALETTE["external"], PALETTE["external_stroke"]),
        "model": ("#E9E3F2", "#6C4D86"),
    }
    fill, stroke = fills.get(role, fills["external"])
    cx, cy = x + w / 2, y + h / 2
    if role == "agent":
        cut = min(22, w * 0.1)
        shape = f'<path d="M {x+cut} {y} H {x+w-cut} L {x+w} {y+h/2} L {x+w-cut} {y+h} H {x+cut} L {x} {y+h/2} Z" fill="{fill}" stroke="{stroke}" stroke-width="3"/>'
    elif role == "human":
        shape = f'<ellipse cx="{cx}" cy="{cy}" rx="{w/2}" ry="{h/2}" fill="{fill}" stroke="{stroke}" stroke-width="3"/>'
    elif role == "memory":
        shape = (
            f'<path d="M {x} {y+12} C {x} {y-4} {x+w} {y-4} {x+w} {y+12} V {y+h-12} '
            f'C {x+w} {y+h+4} {x} {y+h+4} {x} {y+h-12} Z" fill="{fill}" stroke="{stroke}" stroke-width="3"/>'
            f'<path d="M {x} {y+12} C {x} {y+28} {x+w} {y+28} {x+w} {y+12}" fill="none" stroke="{stroke}" stroke-width="3"/>'
        )
    elif role == "model":
        shape = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{fill}" stroke="{stroke}" stroke-width="3"/>'
    elif role == "policy":
        shape = f'<path d="M {cx} {y} L {x+w} {y+18} V {y+h*0.54} Q {cx} {y+h} {cx} {y+h} Q {x} {y+h*0.54} {x} {y+18} Z" fill="{fill}" stroke="{stroke}" stroke-width="3"/>'
    else:
        rx = 24 if role == "tool" else 10
        shape = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="3"/>'
    label_y = cy + (0 if not subtitle else -10)
    text = multiline(cx, label_y, label, 22, weight=720)
    if subtitle:
        text += multiline(cx, cy + 30, subtitle, 14, color=PALETTE["muted"], weight=520)
    return shape + text


def arrow(x1, y1, x2, y2, label=None, style="control", bend=None):
    dash = ""
    stroke = PALETTE["ink"]
    marker = "arrow"
    if style == "data":
        stroke = "#315EA8"
    elif style == "async":
        stroke = "#73558A"
        dash = ' stroke-dasharray="12 9"'
    elif style == "feedback":
        stroke = "#B5472D"
        dash = ' stroke-dasharray="5 7"'
    if bend:
        mx, my = bend
        path = f'M {x1} {y1} Q {mx} {my} {x2} {y2}'
    else:
        path = f'M {x1} {y1} L {x2} {y2}'
    svg = f'<path d="{path}" fill="none" stroke="{stroke}" stroke-width="3"{dash} marker-end="url(#{marker})"/>'
    if label:
        lx = (x1 + x2) / 2 if not bend else bend[0]
        ly = (y1 + y2) / 2 - 10 if not bend else bend[1] - 8
        svg += f'<rect x="{lx-55}" y="{ly-17}" width="110" height="26" rx="13" fill="{PALETTE["paper2"]}"/>'
        svg += multiline(lx, ly + 2, label, 14, color=stroke, weight=650)
    return svg


def boundary(x, y, w, h, label, color="#6B747C", dash=False):
    ds = ' stroke-dasharray="10 8"' if dash else ""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="none" stroke="{color}" stroke-width="2"{ds}/>'
        f'<rect x="{x+20}" y="{y-15}" width="{max(130, len(label)*12)}" height="30" fill="{PALETTE["paper2"]}"/>'
        f'<text x="{x+30}" y="{y+6}" font-size="16" font-weight="700" fill="{color}">{esc(label)}</text>'
    )


def badge(x, y, label, color):
    width = max(88, len(label) * 13 + 30)
    return f'<rect x="{x}" y="{y}" width="{width}" height="34" rx="17" fill="{color}"/><text x="{x+width/2}" y="{y+23}" text-anchor="middle" font-size="15" font-weight="750" fill="#FBF8F1">{esc(label)}</text>'


def scene(pattern):
    k = pattern["topology"]
    s = []
    # Application placement
    if k == "copilot":
        s += [node(80, 250, 170, 100, "业务用户", "human"), node(430, 210, 280, 180, "既有业务应用", "external"), node(840, 250, 220, 100, "Copilot Agent", "agent")]
        s += [arrow(250, 300, 430, 300, "主操作"), arrow(710, 270, 840, 270, "请求"), arrow(840, 330, 710, 330, "建议", "data")]
        s += [badge(446, 170, "决策权在人", LAYER_META["L1"]["color"])]
    elif k == "workflow-participant":
        s += [boundary(90, 170, 1020, 300, "业务流程 / Business Process", PALETTE["workflow_stroke"])]
        xs = [145, 375, 620, 865]
        roles = [("确定性步骤", "workflow"), ("Agent 活动", "agent"), ("人工审批", "human"), ("确定性步骤", "workflow")]
        for x, (lab, role) in zip(xs, roles): s.append(node(x, 260, 170, 100, lab, role))
        for a, b in zip(xs, xs[1:]): s.append(arrow(a+170, 310, b, 310))
    elif k == "front-door":
        s += [node(75, 265, 170, 100, "用户", "human"), node(410, 240, 250, 150, "Hub Agent", "agent", "统一入口")]
        ys = [130, 280, 430]
        for y, lab in zip(ys, ["CRM / 客户域", "ERP / 交易域", "Knowledge / 知识域"]):
            s.append(node(865, y, 240, 90, lab, "external"))
            s.append(arrow(660, 315, 865, y+45, "协调" if y == 280 else None))
        s.append(arrow(245, 315, 410, 315, "意图"))
    elif k == "autonomous-worker":
        s += [node(70, 260, 180, 100, "目标 / 事件", "workflow"), node(420, 220, 250, 180, "自主 Agent", "agent", "长时运行"), node(870, 120, 220, 90, "业务系统", "external"), node(870, 275, 220, 90, "结果", "workflow"), node(870, 430, 220, 90, "人工接管", "human")]
        s += [arrow(250, 310, 420, 310), arrow(670, 275, 870, 165, "行动"), arrow(670, 320, 870, 320, "完成", "data"), arrow(670, 365, 870, 475, "异常", "feedback")]
    elif k == "always-on-worker":
        s += [node(70, 150, 220, 85, "定时器", "workflow", "周期 / 主动跟进"),
              node(440, 150, 260, 85, "人类负责人", "human", "持续委托 · 权限 · 撤销"),
              node(70, 295, 220, 100, "事件收件箱", "workflow", "外部事件 / 用户回复"),
              node(440, 285, 260, 110, "Agent Worker", "agent", "一次有界运行"),
              node(900, 285, 220, 110, "业务系统", "external", "调查 / 受控行动"),
              node(440, 490, 260, 85, "持久状态", "memory", "跨运行进度与记忆"),
              node(900, 490, 220, 85, "按需通知", "workflow", "结果 / 问题 / 审核")]
        s += [arrow(180, 235, 180, 295, "到期事件", "async"),
              arrow(290, 345, 440, 345, "唤醒", "async"),
              arrow(570, 235, 570, 285, "授权 / 撤销"),
              arrow(700, 330, 900, 330, "行动"),
              arrow(700, 370, 900, 532, "按需交付", "async"),
              arrow(470, 490, 470, 395, "读取", "data"),
              arrow(660, 395, 660, 490, "保存", "data"),
              badge(65, 455, "完成 → 待命；职责保留", LAYER_META["L1"]["color"])]
    elif k == "continuous-controller":
        specs = [(75, "业务信号", "external"), (315, "Sense", "workflow"), (555, "Decide", "agent"), (795, "Act", "tool")]
        for x, lab, role in specs: s.append(node(x, 250, 175, 105, lab, role))
        for (x, _, _), (nx, _, _) in zip(specs, specs[1:]): s.append(arrow(x+175, 302, nx, 302))
        s += [node(1000, 250, 150, 105, "环境", "external"), arrow(970, 302, 1000, 302), arrow(1075, 355, 160, 405, "结果反馈", "feedback", (620, 555))]
        s += [node(485, 445, 245, 85, "目标 + 边界 + Override", "human"), arrow(607, 445, 642, 355, "治理", "data")]
    # System organization
    elif k == "single-agent":
        s += [node(455, 235, 290, 170, "Single Agent", "agent", "目标 + 控制 + 状态")]
        for x, y, lab, role in [(90,150,"Tools","tool"),(90,405,"Knowledge","external"),(900,150,"Memory","memory"),(900,405,"Policy","policy")]:
            s.append(node(x,y,190,95,lab,role)); s.append(arrow(455 if x<400 else 745,320,x+190 if x<400 else x,y+47,None,"data"))
    elif k == "workflow-hybrid":
        s += [boundary(70, 150, 1060, 340, "Workflow owns control", PALETTE["workflow_stroke"])]
        specs=[(115,"规则", "workflow"),(320,"Agent 判断","agent"),(545,"人工门禁","human"),(770,"工具动作","tool"),(975,"校验","workflow")]
        for x,lab,role in specs: s.append(node(x,260,140,95,lab,role))
        for (x,_,_), (nx,_,_) in zip(specs,specs[1:]): s.append(arrow(x+140,308,nx,308))
    elif k == "router":
        s += [node(65,270,170,95,"输入","external"), node(430,245,220,145,"Router","workflow","一次分类")]
        for y, lab in zip([120,275,430],["专家 A","专家 B","专家 C"]):
            s.append(node(890,y,190,95,lab,"agent")); s.append(arrow(650,318,890,y+47,"选择" if y==275 else None))
        s.append(arrow(235,318,430,318))
    elif k == "supervisor":
        s += [node(460,145,280,140,"Supervisor","agent","持续协调")]
        for x,lab in zip([110,420,730],["Specialist A","Specialist B","Specialist C"]):
            s.append(node(x,410,240,110,lab,"agent")); s.append(arrow(600,285,x+120,410,"委派" if x==420 else None))
        s.append(node(920,145,190,90,"共享目标","memory")); s.append(arrow(920,190,740,210,None,"data"))
    elif k == "handoff":
        specs=[(95,"Agent A","当前所有者"),(430,"Agent B","接管"),(765,"Agent C / Human","下一所有者")]
        for x,lab,sub in specs: s.append(node(x,245,235,140,lab,"agent" if "Human" not in lab else "human",sub))
        s += [arrow(330,315,430,315,"交接", "async"),arrow(665,315,765,315,"交接", "async")]
        s += [badge(395,445,"控制权沿路径转移",LAYER_META["L2"]["color"])]
    elif k in {"sequence", "chain"}:
        labels = ["Step / Agent A","Step / Agent B","Step / Agent C"] if k=="sequence" else ["Prompt A","Prompt B","Prompt C"]
        role = "agent" if k=="sequence" else "model"
        for x,lab in zip([110,455,800],labels): s.append(node(x,255,230,120,lab,role))
        s += [arrow(340,315,455,315,"输出 → 输入","data"),arrow(685,315,800,315,"输出 → 输入","data")]
    elif k in {"parallel", "fanout"}:
        s += [node(80,270,180,100,"输入 / 主 Agent","agent" if k=="fanout" else "external"), node(930,270,190,100,"聚合 / wait","workflow")]
        for y,lab in zip([120,275,430],["Worker A","Worker B","Worker C"]):
            s.append(node(450,y,220,95,lab,"agent" if k=="fanout" else "model")); s.append(arrow(260,320,450,y+47,"spawn" if k=="fanout" and y==275 else None,"async" if k=="fanout" else "control")); s.append(arrow(670,y+47,930,320,None,"data"))
    elif k == "debate":
        s += [node(100,200,220,115,"Agent A","agent","立场 / 证据"), node(100,380,220,115,"Agent B","agent","反方 / 质询"), node(485,280,230,130,"Debate Space","memory","共享论点"), node(870,280,220,130,"Judge / 共识","agent")]
        s += [arrow(320,258,485,320,"论点","async"),arrow(320,438,485,360,"质询","async"),arrow(715,345,870,345,"裁决")]
    elif k == "group-chat":
        s += [node(465, 120, 270, 105, "Chat Manager", "agent", "选择下一位"), node(430, 300, 340, 115, "Shared Conversation", "memory", "累积线程")]
        for x, lab, role in [(70, "Agent A", "agent"), (870, "Agent B", "agent"), (70, "Human", "human"), (870, "Agent C", "agent")]:
            y = 185 if "A" in lab or "B" in lab else 430
            s.append(node(x, y, 220, 95, lab, role))
            s.append(arrow(x+220 if x < 400 else x, y+47, 430 if x < 400 else 770, 345, "发言", "async"))
        s += [arrow(600, 225, 600, 300, "轮次"), arrow(600, 415, 600, 500, "完成 / 继续", "feedback")]
    elif k == "magentic":
        s += [node(80, 250, 180, 105, "开放目标", "external"), node(390, 130, 260, 120, "Magentic Manager", "agent"), node(390, 395, 260, 120, "Task + Progress Ledger", "memory")]
        s += [arrow(260, 302, 390, 190), arrow(520, 250, 520, 395, "更新账本", "data")]
        for y, lab in [(125, "Research Agent"), (285, "Builder Agent"), (445, "Reviewer Agent")]:
            s.append(node(860, y, 230, 95, lab, "agent")); s.append(arrow(650, 190, 860, y+47, "分派" if y == 285 else None)); s.append(arrow(860, y+78, 650, 455, None, "feedback"))
    elif k == "hierarchy":
        s += [node(470,105,260,110,"Root Supervisor","agent")]
        for x,lab in zip([180,760],["Domain Supervisor A","Domain Supervisor B"]):
            s.append(node(x,300,260,105,lab,"agent")); s.append(arrow(600,215,x+130,300,"分解"))
        for x,lab in zip([80,350,690,960],["Worker A1","Worker A2","Worker B1","Worker B2"]):
            s.append(node(x,500,165,80,lab,"agent")); parent=310 if x<600 else 890; s.append(arrow(parent,405,x+82,500))
    elif k == "peer-network":
        pts=[(250,180,"Agent A"),(730,160,"Agent B"),(860,420,"Agent C"),(390,455,"Agent D")]
        for x,y,lab in pts: s.append(node(x,y,190,95,lab,"agent"))
        edges=[(440,228,730,208),(825,255,955,420),(860,468,580,503),(390,503,345,275),(440,228,860,468)]
        for e in edges: s.append(arrow(*e,style="async"))
        s.append(badge(495,305,"无中央控制者",LAYER_META["L2"]["color"]))
    elif k == "event-choreography":
        s += [node(350, 275, 500, 95, "Event Bus / Domain Events", "memory")]
        for x, y, lab in [(70, 120, "Agent A"), (490, 120, "Agent B"), (910, 120, "Agent C"), (280, 455, "Agent D"), (700, 455, "Agent E")]:
            s.append(node(x, y, 220, 90, lab, "agent"))
            if y < 300: s.append(arrow(x+110, y+90, min(max(x+110, 380), 820), 275, "publish / subscribe", "async"))
            else: s.append(arrow(min(max(x+110, 380), 820), 370, x+110, y, "event", "async"))
        s.append(badge(500, 385, "无同步调用链", LAYER_META["L2"]["color"]))
    elif k == "blackboard":
        s += [node(425, 245, 350, 180, "Shared Blackboard", "memory", "问题 + 证据 + 部分解"), node(475, 105, 250, 90, "Controller", "workflow", "选择下一贡献者")]
        for x, y, lab in [(70, 180, "Research Agent"), (880, 180, "Analysis Agent"), (70, 430, "Builder Agent"), (880, 430, "Reviewer Agent")]:
            s.append(node(x, y, 240, 95, lab, "agent")); s.append(arrow(x+240 if x < 400 else x, y+47, 425 if x < 400 else 775, 335, "read / contribute", "data"))
        s += [arrow(600, 195, 600, 245, "调度"), badge(485, 465, "共享状态协作", LAYER_META["L2"]["color"])]
    elif k == "inline-subagent":
        s += [node(130,240,270,150,"Main Agent","agent"), boundary(690,180,360,270,"call_agent tool boundary",PALETTE["agent_stroke"],True), node(760,260,220,110,"一次性 Subagent","agent")]
        s += [arrow(400,285,690,285,"task"),arrow(690,350,400,350,"single result","data")]
    elif k == "agent-pool":
        s += [node(90,250,230,130,"Main Agent","agent","Coordinator"), node(450,265,230,100,"Message Bus","memory")]
        for y,lab in zip([105,275,445],["Researcher","Writer","Reviewer"]):
            s.append(node(880,y,210,95,lab,"agent")); s.append(arrow(680,315,880,y+47,None,"async"))
        s.append(arrow(320,315,450,315,"send / wait","async"))
    elif k == "team":
        s += [node(70,275,190,100,"Main Agent","agent","设定目标"), node(470,105,210,95,"Planner","agent"), node(810,275,210,95,"Builder","agent"), node(470,455,210,95,"Reviewer","agent")]
        s += [arrow(260,325,470,152,"kickoff"),arrow(680,152,810,323,"直接消息","async"),arrow(810,370,680,502,"评审请求","async"),arrow(470,502,260,345,"最终报告","data"),arrow(575,455,575,200,None,"feedback")]
    # Agent control
    elif k in {"reactive", "react"}:
        if k == "reactive":
            s += [node(120,255,230,120,"环境观察","external"),node(485,235,230,160,"Agent Policy","agent"),node(850,255,230,120,"环境动作","tool")]
            s += [arrow(350,315,485,315),arrow(715,315,850,315),arrow(965,375,235,375,"反馈","feedback",(600,570))]
        else:
            pts=[(490,120,"思考","model"),(820,300,"行动","tool"),(490,470,"观察","external"),(160,300,"更新状态","memory")]
            for x,y,lab,role in pts:s.append(node(x,y,220,95,lab,role))
            s += [arrow(710,168,820,347),arrow(820,347,710,518),arrow(490,518,380,347),arrow(380,347,490,168)]
            s.append(badge(482,305,"直到完成 / 停止",LAYER_META["L3"]["color"]))
    elif k == "plan-execute":
        s += [node(80,275,180,100,"目标","external"),node(390,170,230,120,"Planner","agent"),node(390,390,230,100,"Plan Store","memory"),node(810,240,250,150,"Executor","agent")]
        s += [arrow(260,325,390,230),arrow(505,290,505,390,"计划","data"),arrow(620,440,810,345,"下一步","data"),arrow(810,275,620,230,"重规划","feedback")]
    elif k == "bdi":
        s += [node(70, 265, 180, 100, "观察", "external"), node(335, 120, 230, 95, "Beliefs", "memory"), node(335, 275, 230, 95, "Desires", "external"), node(335, 430, 230, 95, "Intentions", "memory")]
        s += [node(690, 230, 250, 165, "Deliberator", "agent", "选择 + 承诺 + 重议"), node(1010, 265, 150, 100, "行动", "tool")]
        s += [arrow(250, 315, 335, 168, "更新", "data"), arrow(565, 168, 690, 275), arrow(565, 322, 690, 312), arrow(565, 478, 690, 350), arrow(940, 312, 1010, 315), arrow(1085, 365, 450, 525, "结果 / 重议", "feedback", (820, 570))]
    elif k in {"reflection", "evaluator"}:
        left="Generator" if k=="evaluator" else "Actor / Draft"
        right="Evaluator" if k=="evaluator" else "Critic / Reflection"
        s += [node(160,250,250,130,left,"agent"),node(770,250,250,130,right,"agent"),node(465,445,250,95,"通过 / 最终输出","workflow")]
        s += [arrow(410,315,770,315,"候选"),arrow(770,370,410,370,"反馈","feedback"),arrow(600,380,600,445,"达标","data")]
    elif k == "goal-monitoring":
        s += [node(80,130,220,95,"总目标","external"),node(80,280,220,95,"子目标栈","memory"),node(440,235,260,150,"Agent","agent"),node(850,135,220,95,"环境状态","external"),node(850,380,220,105,"Progress Monitor","workflow")]
        s += [arrow(300,178,440,275),arrow(300,328,440,345,"下一目标","data"),arrow(700,285,850,182,"行动"),arrow(850,432,700,355,"偏差 / 完成","feedback")]
    elif k == "learning":
        s += [node(80,260,220,110,"Agent 执行","agent"),node(420,130,230,100,"结果与反馈","external"),node(420,390,230,105,"经验库","memory"),node(820,260,240,110,"策略更新","workflow")]
        s += [arrow(300,315,420,180,"结果"),arrow(535,230,535,390,"沉淀","data"),arrow(650,442,820,335,"抽象"),arrow(820,280,300,280,"影响未来","feedback",(600,80))]
    elif k == "resource-aware":
        s += [node(70,270,190,100,"任务","external"),node(380,235,240,170,"资源策略","workflow","成本 / 延迟 / 风险")]
        for y,lab,sub in [(110,"Fast Model","低成本"),(285,"Strong Model","高质量"),(460,"Human / Queue","受限资源")]:
            s.append(node(850,y,230,100,lab,"model" if "Model" in lab else "human",sub));s.append(arrow(620,320,850,y+50,"选择" if y==285 else None))
        s.append(arrow(260,320,380,320))
    elif k == "reasoning":
        s += [node(70,275,190,100,"问题","external"),node(360,245,210,150,"策略选择","agent")]
        for y,lab in [(100,"CoT 线性推演"),(260,"ToT 分支搜索"),(420,"多样采样 / 投票")]:
            s.append(node(760,y,270,95,lab,"model")); s.append(arrow(570,320,760,y+47,None,"data"))
        s.append(node(1040,275,120,100,"答案","workflow"))
    elif k == "prioritization":
        for y,lab in zip([150,280,410],["任务 A","任务 B","任务 C"]): s.append(node(70,y,170,80,lab,"external"))
        s += [node(390,240,250,150,"Priority Scorer","agent","价值 × 紧迫 × 风险"),node(810,190,250,95,"现在执行","workflow"),node(810,360,250,95,"排队 / 延后","memory")]
        for y in [190,320,450]: s.append(arrow(240,y,390,315))
        s += [arrow(640,285,810,238,"Top"),arrow(640,355,810,408,"Rest","data")]
    elif k == "exploration":
        s += [node(75,270,180,95,"问题空间","external"),node(350,255,210,125,"Explorer","agent")]
        for x,y,lab in [(760,95,"候选 A"),(920,240,"候选 B"),(760,430,"候选 C")]:
            s.append(node(x,y,180,85,lab,"workflow")); s.append(arrow(560,318,x,y+42,"探索" if lab=="候选 B" else None,"data"))
        s.append(node(1030,440,130,80,"证据","external")); s.append(arrow(940,472,1030,480)); s.append(arrow(1030,440,560,370,"剪枝 / 扩展","feedback",(800,590)))
    # Mechanisms
    elif k == "tool-use":
        s += [node(100,255,240,130,"Agent","agent"),node(470,250,220,140,"Tool Runtime","workflow")]
        for y,lab in zip([105,275,445],["Search","Database","Business API"]):
            s.append(node(875,y,220,90,lab,"tool")); s.append(arrow(690,320,875,y+45,"调用" if y==275 else None))
        s += [arrow(340,290,470,290,"name + args"),arrow(470,355,340,355,"result","data")]
    elif k == "memory":
        s += [node(80,265,220,115,"Agent","agent"),node(420,245,220,150,"Memory Manager","workflow")]
        for y,lab in zip([100,275,450],["Working Memory","Episodic Memory","Semantic Memory"]):
            s.append(node(840,y,250,95,lab,"memory")); s.append(arrow(640,320,840,y+47,"读 / 写" if y==275 else None,"data"))
        s.append(arrow(300,322,420,322,None,"data"))
    elif k == "mcp":
        s += [boundary(55,140,350,350,"MCP Host",PALETTE["agent_stroke"]),node(115,250,230,120,"Agent Application","agent"),node(455,250,220,120,"MCP Client","workflow")]
        s.append(arrow(345,310,455,310,"请求"))
        for y,lab in zip([100,265,430],["Tools","Resources","Prompts"]):
            s.append(node(845,y,250,95,f"MCP Server · {lab}","external"));s.append(arrow(675,310,845,y+47,"JSON-RPC" if y==265 else None,"data"))
    elif k == "exception":
        s += [node(60,270,180,95,"执行步骤","workflow"),node(360,230,220,175,"失败分类","policy","瞬态 / 永久 / 高风险")]
        for y,lab,role in [(95,"Retry + Backoff","workflow"),(250,"Fallback / Degrade","workflow"),(405,"Human Escalation","human")]:
            s.append(node(820,y,250,100,lab,role));s.append(arrow(580,318,820,y+50,"选择" if y==250 else None,"feedback"))
        s.append(arrow(240,318,360,318))
    elif k == "hitl":
        s += [node(80,270,220,100,"Agent 提案","agent"),node(420,230,240,180,"Risk / Confidence Gate","policy"),node(840,120,220,100,"继续执行","workflow"),node(840,390,220,110,"人工审批","human")]
        s += [arrow(300,320,420,320),arrow(660,280,840,170,"低风险"),arrow(660,360,840,445,"高风险"),arrow(840,445,660,360,"批准 / 修改","feedback")]
    elif k == "rag":
        s += [node(45,270,160,90,"查询","external"),node(300,250,200,130,"Retriever","workflow"),node(585,105,230,95,"Knowledge Base","memory"),node(585,405,230,95,"Context Builder","workflow"),node(920,250,220,130,"LLM / Agent","model")]
        s += [arrow(205,315,300,315),arrow(400,250,650,200,"检索"),arrow(700,200,700,405,"片段","data"),arrow(815,452,920,355,"上下文","data"),arrow(500,345,585,452,"问题","data")]
    elif k == "agentic-rag":
        s += [node(55, 270, 160, 90, "复杂问题", "external"), node(310, 235, 230, 160, "Retrieval Agent", "agent", "计划 + 选择来源")]
        for y, lab in [(105, "Search / Web"), (270, "Enterprise KB"), (435, "Database")]:
            s.append(node(710, y, 230, 90, lab, "tool")); s.append(arrow(540, 315, 710, y+45, "query" if y == 270 else None))
        s += [node(980, 245, 180, 140, "Sufficiency Gate", "policy"), arrow(940, 315, 980, 315, "evidence", "data"), arrow(1070, 385, 425, 440, "不足 → 再查询", "feedback", (760, 555)), badge(980, 415, "充分 → 生成", LAYER_META["L3"]["color"])]
    elif k == "a2a":
        s += [boundary(55,150,410,340,"A2A Client Side",PALETTE["agent_stroke"]),node(125,255,270,120,"Client Agent","agent"),boundary(735,150,410,340,"A2A Server Side",PALETTE["workflow_stroke"]),node(805,255,270,120,"Remote Agent","agent")]
        s += [node(500,110,200,80,"AgentCard","external"),node(500,275,200,80,"Message / Task","workflow"),node(500,440,200,80,"Artifact / Update","external")]
        s += [arrow(600,190,260,255,"发现","data"),arrow(465,315,500,315),arrow(700,315,735,315),arrow(735,480,700,480,"返回","data")]
    elif k == "guardrails":
        specs=[(55,"Input Guard","policy"),(300,"Agent","agent"),(570,"Tool Guard","policy"),(825,"Output Guard","policy")]
        for x,lab,role in specs:s.append(node(x,255,190,120,lab,role))
        for (x,_,_), (nx,_,_) in zip(specs,specs[1:]):s.append(arrow(x+190,315,nx,315))
        s += [node(450,465,250,90,"Policy + Audit","memory"),arrow(575,465,575,375,"规则 / 记录","data")]
    elif k == "identity-policy":
        s += [node(55, 165, 200, 95, "User Identity", "human"), node(55, 405, 200, 95, "Agent Identity", "agent"), node(355, 230, 260, 170, "Policy Enforcement Point", "policy", "user + agent + task")]
        s += [node(705, 115, 230, 95, "Token Service", "workflow", "short-lived"), node(705, 285, 230, 95, "Tool Gateway", "workflow"), node(705, 455, 230, 95, "Audit Log", "memory"), node(1010, 285, 150, 95, "Resource", "external")]
        s += [arrow(255, 212, 355, 275, "代表谁", "data"), arrow(255, 452, 355, 355, "谁行动", "data"), arrow(615, 275, 705, 162, "JIT scope"), arrow(615, 335, 705, 332, "allow / deny"), arrow(935, 332, 1010, 332), arrow(820, 380, 820, 455, "记录", "data")]
    elif k == "agent-registry":
        s += [node(60, 270, 190, 100, "Task / Caller", "agent"), node(360, 225, 260, 190, "Agent Registry", "memory", "contract + version + owner + health")]
        for y, lab in [(105, "Agent A · v2"), (275, "Agent B · v4"), (445, "Agent C · v1")]:
            s.append(node(830, y, 250, 95, lab, "agent")); s.append(arrow(620, 320, 830, y+47, "resolve" if y == 275 else None, "data"))
        s += [arrow(250, 320, 360, 320, "discover"), badge(455, 445, "信任 + 兼容 + 健康", LAYER_META["L3"]["color"])]
    elif k == "durable-execution":
        s += [node(55, 270, 175, 95, "Start / Resume", "external"), node(330, 235, 230, 165, "Durable Runtime", "workflow", "deterministic replay"), node(690, 105, 220, 90, "Agent Step", "agent"), node(690, 275, 220, 90, "Tool Step", "tool"), node(690, 445, 220, 90, "Human / Callback", "human"), node(990, 235, 170, 165, "History + Checkpoint", "memory")]
        s += [arrow(230, 317, 330, 317), arrow(560, 280, 690, 150), arrow(560, 317, 690, 320), arrow(560, 355, 690, 490), arrow(910, 150, 990, 275, "record", "data"), arrow(910, 320, 990, 317, "record", "data"), arrow(910, 490, 990, 360, "resume", "feedback"), arrow(990, 400, 445, 455, "replay", "feedback", (760, 555))]
    elif k == "saga":
        xs = [65, 325, 585, 845]
        for x, lab in zip(xs, ["T1 · Reserve", "T2 · Charge", "Pivot", "T4 · Notify"]): s.append(node(x, 205, 210, 95, lab, "workflow"))
        for x, lab in zip(xs[:2], ["C1 · Release", "C2 · Refund"]): s.append(node(x, 420, 210, 85, lab, "workflow"))
        for x, nx in zip(xs, xs[1:]): s.append(arrow(x+210, 252, nx, 252, "commit"))
        s += [arrow(430, 300, 430, 420, "failure", "feedback"), arrow(325, 462, 275, 462, "compensate", "feedback"), badge(600, 345, "Pivot 后只允许幂等重试 / 人工处置", LAYER_META["L3"]["color"])]
    elif k == "evaluation":
        s += [node(65,250,200,120,"Agent Run","agent"),node(390,245,220,130,"Trace / Dataset","memory"),node(740,130,240,100,"Automated Evals","workflow"),node(740,390,240,100,"Human Review","human"),node(1015,260,140,110,"改进","workflow")]
        s += [arrow(265,310,390,310,"记录","data"),arrow(610,280,740,180),arrow(610,340,740,440),arrow(980,180,1085,260,"指标"),arrow(980,440,1085,370,"反馈","feedback")]
    elif k == "context":
        for y,lab,role in [(90,"Instructions","policy"),(230,"History","memory"),(370,"Retrieved Docs","external"),(510,"Tool Results","tool")]:s.append(node(55,y,220,75,lab,role))
        s += [node(385,245,220,150,"Select","workflow"),node(690,245,220,150,"Compress + Assemble","workflow"),node(1000,260,150,120,"Model","model")]
        for y in [128,268,408,548]:s.append(arrow(275,y,385,320,None,"data"))
        s += [arrow(605,320,690,320,"relevant only","data"),arrow(910,320,1000,320,"context","data")]
    elif k == "prompting":
        s += [boundary(75,120,720,420,"Prompt Construction",PALETTE["tool_stroke"]),node(130,180,210,85,"Instruction","policy"),node(130,315,210,85,"Examples","external"),node(130,450,210,85,"Output Schema","workflow"),node(470,180,240,85,"Role + Context","memory"),node(470,315,240,85,"Reasoning Cue","workflow"),node(470,450,240,85,"User Input","external"),node(900,260,220,140,"LLM","model")]
        for x,y in [(340,222),(340,357),(340,492),(710,222),(710,357),(710,492)]:s.append(arrow(x,y,900,330,None,"data"))
    elif k == "skills":
        s += [node(75,260,220,120,"Agent Host","agent"),boundary(425,125,430,410,"Skill Package",PALETTE["tool_stroke"]),node(490,175,300,85,"SKILL.md","policy"),node(490,300,300,85,"scripts/","tool"),node(490,425,300,85,"references/ + assets/","external"),node(950,260,190,120,"Task Result","workflow")]
        s += [arrow(295,320,425,320,"按需加载","data"),arrow(855,320,950,320,"执行")]
    else:
        s += [node(140,255,250,120,"Input","external"),node(475,235,250,160,pattern["name_en"],"agent"),node(810,255,250,120,"Output","workflow"),arrow(390,315,475,315),arrow(725,315,810,315)]
    return "".join(s)


def source_caption(pattern):
    labels=[]
    for sid in pattern["sources"][:2]:
        src=SOURCES[sid]
        locator = pattern.get("source_locators", {}).get(sid, "")
        if sid.startswith("adp-") and sid[4:].isdigit():
            section = public_locator(locator)
            labels.append(f"Gullí 2025, Ch. {sid[4:]}" + (f", {section}" if section else ""))
        elif sid=="adp-intro": labels.append("Gullí 2025, Introduction")
        elif sid=="adp-appendix-a":
            section = public_locator(locator)
            if section == "Appendix A technique family":
                section = "Advanced Prompting Techniques"
            labels.append("Gullí 2025, Appendix A" + (f", {section}" if section and section != "Appendix A" else ""))
        elif sid=="schmid-subagents": labels.append("Schmid 2026, " + (locator.split(":", 1)[0] if locator else "Four Subagent Patterns"))
        elif sid=="anthropic-agents": labels.append("Anthropic, Building Effective Agents")
        elif sid=="anthropic-always-on": labels.append("Anthropic 2026, Building always-on agents")
        elif sid=="lang-ambient-agents": labels.append("LangChain 2025, Introducing ambient agents")
        elif sid.startswith("ms-"): labels.append(f'{src["author"]}, {src["title"]}')
        elif sid.startswith("lang-"): labels.append(f'LangChain Docs, {src["title"]}')
        elif sid=="react-paper": labels.append("Yao et al. 2022, ReAct")
        elif sid=="mcp-architecture": labels.append("MCP Specification 2026-07-28")
        elif sid=="a2a-spec": labels.append("A2A Specification v1.0.0")
        elif sid=="agent-skills-spec": labels.append("Agent Skills Specification, accessed 2026-08-08")
        else: labels.append(src["title"])
    return " · ".join(labels)


def render_svg(pattern):
    layer = pattern["layer"]
    meta = LAYER_META.get(layer, ENABLER_META)
    section_label = layer if layer in LAYER_META else ENABLER_META["label"]
    title = f'{pattern["name_en"]} · {pattern["name_zh"]}'
    desc = f'{pattern["participants"]} {pattern["relationships"]}'
    uid = pattern["id"]
    diagram_scene = scene(pattern).replace('url(#arrow)', f'url(#arrow-{uid})')
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 675" role="img" aria-labelledby="title-{uid} desc-{uid}">
  <title id="title-{uid}">{esc(title)}</title>
  <desc id="desc-{uid}">{esc(desc)}</desc>
  <defs>
    <marker id="arrow-{uid}" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="context-stroke"/></marker>
  </defs>
  <rect width="1200" height="675" fill="{PALETTE['paper2']}"/>
  <rect x="0" y="0" width="16" height="675" fill="{meta['color']}"/>
  <text x="55" y="54" font-family="Avenir Next, PingFang SC, Microsoft YaHei, sans-serif" font-size="15" font-weight="750" letter-spacing="1.5" fill="{meta['color']}">{section_label} · {esc(meta['title'].upper())}</text>
  <text x="55" y="94" font-family="Iowan Old Style, Avenir Next, serif" font-size="31" font-weight="700" fill="{PALETTE['ink']}">{esc(pattern['name_en'])}</text>
  <text x="1145" y="90" text-anchor="end" font-family="Avenir Next, PingFang SC, sans-serif" font-size="16" font-weight="560" fill="{PALETTE['muted']}">{esc(pattern['name_zh'])}</text>
  <g font-family="Avenir Next, PingFang SC, Microsoft YaHei, sans-serif">{diagram_scene}</g>
  <line x1="55" y1="615" x2="1145" y2="615" stroke="#C8C4BB" stroke-width="1"/>
  <text x="55" y="646" font-family="Avenir Next, PingFang SC, sans-serif" font-size="14" fill="{PALETTE['muted']}">出处：{esc(source_caption(pattern))}</text>
  <text x="1145" y="646" text-anchor="end" font-family="Avenir Next, PingFang SC, sans-serif" font-size="13" fill="{PALETTE['muted']}">Atlas v{BLOG['version']} · topology redrawn by this article</text>
</svg>'''


def render_layer_map():
    widths=[980,780,580]
    body=[]
    for i,(layer,meta) in enumerate(LAYER_META.items()):
        w=widths[i]; x=(1200-w)/2; y=120+i*120
        body.append(f'<rect x="{x}" y="{y}" width="{w}" height="92" rx="8" fill="{meta["color"]}" opacity="{0.92-i*0.05}"/>')
        body.append(f'<text x="{x+30}" y="{y+38}" font-size="20" font-weight="800" fill="#FBF8F1">{layer} · {esc(meta["title"])}</text>')
        body.append(f'<text x="{x+30}" y="{y+67}" font-size="15" font-weight="560" fill="#FBF8F1">{esc(meta["question"])}</text>')
        body.append(f'<text x="{x+w-25}" y="{y+56}" text-anchor="end" font-size="31" font-weight="800" fill="#FBF8F1">{sum(p["layer"]==layer for p in PATTERNS)}</text>')
    enabler_count = sum(pattern["catalog_type"] == "enabler" for pattern in PATTERNS)
    body.append(f'<rect x="110" y="505" width="980" height="92" rx="8" fill="{ENABLER_META["color"]}" opacity=".16" stroke="{ENABLER_META["color"]}" stroke-width="2"/>')
    body.append(f'<text x="140" y="543" font-size="20" font-weight="800" fill="{ENABLER_META["color"]}">ENABLERS · {esc(ENABLER_META["title"])}</text>')
    body.append(f'<text x="140" y="572" font-size="15" font-weight="560" fill="{PALETTE["muted"]}">{esc(ENABLER_META["question"])}</text>')
    body.append(f'<text x="1060" y="560" text-anchor="end" font-size="31" font-weight="800" fill="{ENABLER_META["color"]}">{enabler_count}</text>')
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 675" role="img" aria-labelledby="title desc">
<title id="title">Agentic Pattern 三层认知地图与实现手段</title><desc id="desc">L1 Application、L2 Architecture、L3 Design 构成三个 Pattern 层级；Techniques、Protocols 与 Practices 作为实现手段单独列出，不构成第四层 Pattern。</desc>
<rect width="1200" height="675" fill="{PALETTE['paper2']}"/><text x="60" y="62" font-family="Iowan Old Style, Songti SC, serif" font-size="34" font-weight="700" fill="{PALETTE['ink']}">先确定 System of Interest，再讨论 Pattern</text>
<text x="60" y="92" font-family="Avenir Next, PingFang SC, sans-serif" font-size="16" fill="{PALETTE['muted']}">三层回答可复用结构；底部实现手段不编号，也不作为 Pattern 计数。</text>
<g font-family="Avenir Next, PingFang SC, sans-serif">{''.join(body)}</g>
</svg>'''


def render_l1_relative_map():
    """Render a qualitative map of the four request/work-item L1 patterns."""
    points = [
        ("Workflow Participant", "流程参与者", 315, 455, "start"),
        ("Embedded Copilot", "嵌入式副驾驶", 950, 505, "end"),
        ("Agentic Front Door", "Agent 化统一入口", 815, 300, "end"),
        ("Autonomous Agent Worker", "自主后台工作者", 390, 185, "start"),
    ]
    marks = []
    for name_en, name_zh, x, y, side in points:
        direction = 1 if side == "start" else -1
        label_x = x + direction * 24
        marks.append(
            f'<line x1="{x}" y1="{y}" x2="{x + direction * 16}" y2="{y}" stroke="{PALETTE["line"]}" stroke-width="1"/>'
            f'<circle cx="{x}" cy="{y}" r="10" fill="{LAYER_META["L1"]["color"]}" stroke="{PALETTE["ink"]}" stroke-width="2"/>'
            f'<text x="{label_x}" y="{y-7}" text-anchor="{side}" font-size="19" font-weight="760" fill="{PALETTE["ink"]}">{esc(name_en)}</text>'
            f'<text x="{label_x}" y="{y+16}" text-anchor="{side}" font-size="14" font-weight="520" fill="{PALETTE["muted"]}">{esc(name_zh)}</text>'
        )
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 675" role="img" aria-labelledby="title-l1-map desc-l1-map">
  <title id="title-l1-map">L1 人机协作 Pattern 相对性质定位</title>
  <desc id="desc-l1-map">横轴从人与执行过程低耦合到高耦合，纵轴从 Agent 低任务推进自主度到高自主度。流程参与者位于左下，嵌入式副驾驶位于右下，Agent 化统一入口位于右上偏中，自主后台工作者位于左上。位置只表达相对倾向，不是定量评分。</desc>
  <rect width="1200" height="675" fill="{PALETTE['paper2']}"/>
  <text x="60" y="58" font-family="Avenir Next, PingFang SC, sans-serif" font-size="14" font-weight="800" letter-spacing="2" fill="{LAYER_META['L1']['color']}">L1 SYNTHESIS · QUALITATIVE MAP</text>
  <text x="60" y="96" font-family="Iowan Old Style, Songti SC, serif" font-size="31" font-weight="700" fill="{PALETTE['ink']}">工作中的人有多近，Agent 又能走多远？</text>
  <text x="60" y="126" font-family="Avenir Next, PingFang SC, sans-serif" font-size="14" fill="{PALETTE['muted']}">位置只表达四个 Pattern 之间的相对高低与邻近关系，不代表定量评分或严格边界。</text>
  <rect x="185" y="155" width="900" height="390" fill="none" stroke="{PALETTE['line']}" stroke-width="1"/>
  <line x1="635" y1="155" x2="635" y2="545" stroke="{PALETTE['line']}" stroke-width="1" stroke-dasharray="5 7" opacity=".55"/>
  <line x1="185" y1="350" x2="1085" y2="350" stroke="{PALETTE['line']}" stroke-width="1" stroke-dasharray="5 7" opacity=".55"/>
  <g font-family="Avenir Next, PingFang SC, sans-serif">{''.join(marks)}</g>
  <text x="185" y="574" font-family="Avenir Next, PingFang SC, sans-serif" font-size="13" fill="{PALETTE['muted']}">低 · 人无需持续在场</text>
  <text x="1085" y="574" text-anchor="end" font-family="Avenir Next, PingFang SC, sans-serif" font-size="13" fill="{PALETTE['muted']}">高 · 人持续参与</text>
  <text x="635" y="615" text-anchor="middle" font-family="Avenir Next, PingFang SC, sans-serif" font-size="16" font-weight="750" fill="{PALETTE['ink']}">人与执行过程的耦合程度</text>
  <text x="154" y="535" text-anchor="end" font-family="Avenir Next, PingFang SC, sans-serif" font-size="13" fill="{PALETTE['muted']}">低</text>
  <text x="154" y="169" text-anchor="end" font-family="Avenir Next, PingFang SC, sans-serif" font-size="13" fill="{PALETTE['muted']}">高</text>
  <text x="80" y="350" text-anchor="middle" transform="rotate(-90 80 350)" font-family="Avenir Next, PingFang SC, sans-serif" font-size="16" font-weight="750" fill="{PALETTE['ink']}">Agent 的任务推进自主度</text>
  <text x="1140" y="650" text-anchor="end" font-family="Avenir Next, PingFang SC, sans-serif" font-size="12" fill="{PALETTE['muted']}">Continuous Controller 不在此图：它处理持续环境反馈闭环，而非一次请求或有界工作项。</text>
</svg>'''


def render_legend():
    items=[("Human","human"),("Agent","agent"),("Workflow","workflow"),("Model","model"),("Tool","tool"),("Memory / State","memory"),("Policy","policy"),("External System","external")]
    parts=[]
    for i,(lab,role) in enumerate(items):
        col=i%4; row=i//4; parts.append(node(70+col*285,160+row*180,210,85,lab,role))
    parts += [arrow(120,570,300,570,"控制"),arrow(390,570,570,570,"数据","data"),arrow(660,570,840,570,"异步","async"),arrow(930,570,1110,570,"反馈","feedback")]
    legend_scene=''.join(parts).replace('url(#arrow)','url(#arrow-legend)')
    return f'''<?xml version="1.0" encoding="UTF-8"?><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 675" role="img" aria-labelledby="title-legend desc-legend"><title id="title-legend">视觉语法图例</title><desc id="desc-legend">全文实体形状和关系线型。</desc><defs><marker id="arrow-legend" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="context-stroke"/></marker></defs><rect width="1200" height="675" fill="{PALETTE['paper2']}"/><text x="60" y="70" font-family="Iowan Old Style, Songti SC, serif" font-size="34" font-weight="700" fill="{PALETTE['ink']}">一套视觉语法，贯穿所有 Pattern</text><g font-family="Avenir Next, PingFang SC, sans-serif">{legend_scene}</g></svg>'''


def public_locator(locator):
    """Remove private research-file pagination from public-facing citations."""
    detail = re.sub(r'[；;]\s*研究用 PDF 物理页\s*[0-9、–—-]+', '', str(locator))
    detail = re.sub(r'研究用 PDF 物理页\s*[0-9、–—-]+[；;]?', '', detail)
    return detail.strip().strip('；;·').strip()


def source_note(source, locator=None):
    detail = public_locator(locator or source["locator"])
    accessed = source.get("accessed_at")
    book_types = {"official book", "official book chapter", "official book section", "paper"}
    return f'{detail} · accessed {accessed}' if accessed and source["type"] not in book_types else detail


def cite_html(pattern):
    blocks=[]
    adp_sources = [sid for sid in pattern["sources"] if sid.startswith("adp-")]
    if adp_sources:
        official = SOURCES["adp-official"]
        locators = []
        for sid in adp_sources:
            src = SOURCES[sid]
            locator = public_locator(pattern.get("source_locators", {}).get(sid, src["locator"]))
            if sid.startswith("adp-") and sid[4:].isdigit() and not locator.startswith("Chapter"):
                locator = f"Chapter {sid[4:]} · {locator}"
            elif sid == "adp-intro" and not locator.startswith("Introduction"):
                locator = f"Introduction · {locator}"
            elif sid == "adp-appendix-a" and not locator.startswith("Appendix A"):
                locator = f"Appendix A · {locator}"
            if locator not in locators:
                locators.append(locator)
        blocks.append(f'<a href="{esc(official["url"])}" target="_blank" rel="noopener noreferrer"><span>{esc(official["author"])} · Agentic Design Patterns</span>{esc("；".join(locators))}</a>')
    for sid in pattern["sources"]:
        if sid.startswith("adp-"):
            continue
        src=SOURCES[sid]
        locator = public_locator(pattern.get("source_locators", {}).get(sid, src["locator"]))
        blocks.append(f'<a href="{esc(src["url"])}" target="_blank" rel="noopener noreferrer"><span>{esc(src["author"])}</span>{esc(source_note(src, locator))}</a>')
    return "".join(blocks)


def pattern_html(pattern, index):
    aliases=" · ".join(pattern["aliases"]) if pattern["aliases"] else "—"
    technique=""
    if pattern["techniques"]:
        technique='<div class="technique-strip" aria-label="包含技术">'+"".join(f'<span>{esc(t)}</span>' for t in pattern["techniques"])+"</div>"
    return f'''
<article class="pattern-entry layer-{pattern['layer'].lower()}" id="{pattern['id']}">
  <div class="pattern-kicker"><span>{pattern['layer']}</span><span>{esc(pattern['kind'])}</span><span>{index:02d}</span></div>
  <header class="pattern-heading">
    <div><h3 lang="en">{esc(pattern['name_en'])}</h3><p class="localized-name" lang="zh-Hans">{esc(pattern['name_zh'])}</p></div>
    <p class="intent">{esc(pattern['intent'])}</p>
  </header>
  <figure class="topology"><a href="diagrams/{pattern['id']}.svg" aria-label="打开 {esc(pattern['name_zh'])} 独立 SVG"><img src="diagrams/{pattern['id']}.svg" alt="{esc(pattern['name_zh'])}静态拓扑图"></a><figcaption>静态拓扑优先；虚线表示异步或反馈关系。点击图形可打开独立 SVG。</figcaption></figure>
  <div class="pattern-notes">
    <section><h4>适用信号</h4><p>{esc(pattern['when'])}</p></section>
    <section><h4>带来的能力</h4><p>{esc(pattern['strength'])}</p></section>
    <section><h4>主要代价</h4><p>{esc(pattern['cost'])}</p></section>
  </div>
  <div class="boundary-note"><div><span>别名</span><p>{esc(aliases)}</p></div><div><span>不要混淆</span><p>{esc(pattern['confusion'])}</p></div><div><span>本文归类</span><p>{esc(pattern['classification'])}</p></div></div>
  {technique}
  <footer class="pattern-sources"><span>出处</span>{cite_html(pattern)}</footer>
</article>'''


def coverage_table_html():
    chapter_to_pattern={}
    for pattern in PATTERNS:
        if pattern["book_chapter"]:
            chapter_to_pattern.setdefault(pattern["book_chapter"],[]).append(pattern)
    # Chapters represented through variants/families rather than the book_chapter flag.
    fallback={5:"tool-use",7:"supervisor-specialist",8:"memory-management",9:"learning-adaptation",10:"mcp",12:"exception-recovery",13:"human-in-loop",14:"rag",15:"a2a",16:"resource-aware",18:"guardrails",19:"evaluation-monitoring"}
    by_id={p["id"]:p for p in PATTERNS}
    rows=[]
    for n,title,start,end in CHAPTERS:
        pats=chapter_to_pattern.get(n,[])
        if not pats and n in fallback:pats=[by_id[fallback[n]]]
        links=", ".join(f'<a class="bilingual-name-inline" href="#{p["id"]}">{bilingual_name(p)}</a>' for p in pats)
        layer=" / ".join(sorted({p["layer"] for p in pats}))
        kind="；".join(sorted({p["kind"] for p in pats}))
        rows.append(f'<tr><td>{n:02d}</td><td>{esc(title.replace("_","/"))}</td><td><span class="layer-token {layer.lower().replace(" / "," ")}">{layer}</span></td><td>{links}</td><td>{esc(kind)}</td><td>PDF {start}-{end}</td></tr>')
    return "".join(rows)


def render_index():
    nav=[]; sections=[]; count=0
    for layer,meta in LAYER_META.items():
        layer_patterns=[p for p in PATTERNS if p["layer"]==layer]
        nav.append(f'<a href="#{layer.lower()}"><b>{layer}</b><span>{esc(meta["title"])}</span><em>{len(layer_patterns)}</em></a>')
        entries=[]
        for pattern in layer_patterns:
            count+=1; entries.append(pattern_html(pattern,count))
        sections.append(f'''<section class="layer-section {layer.lower()}" id="{layer.lower()}">
<header class="layer-header"><span class="layer-number">{layer}</span><div><p>System of Interest</p><h2>{esc(meta['title'])}</h2><blockquote>{esc(meta['question'])}</blockquote></div><span class="layer-count">{len(layer_patterns)}<small>entries</small></span></header>
{''.join(entries)}</section>''')
    sources="".join(f'<li id="source-{esc(sid)}"><span>{esc(src["type"])}</span><a href="{esc(src["url"])}" target="_blank" rel="noreferrer">{esc(src["title"])}</a><p>{esc(src["author"])} · {esc(src["locator"])}</p></li>' for sid,src in SOURCES.items())
    return f'''<!doctype html>
<html lang="zh-Hans"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="按三层 System of Interest 与独立实现手段目录重组的 Agentic AI Pattern 视觉图鉴。"><title>Agentic Pattern 视觉图鉴</title><link rel="stylesheet" href="assets/article.css"></head>
<body><a class="skip-link" href="#main">跳到正文</a>
<header class="hero"><div class="hero-grid"><div class="edition">FIELD GUIDE · 2026</div><div class="hero-copy"><p class="eyebrow">Agentic AI 应用架构模式</p><h1>先看见结构，<br>再谈论 Pattern。</h1><p class="deck">面向视觉空间学习者的架构图鉴：以静态拓扑为主，把 {len(PATTERNS)} 个架构、设计、机制、协议与技术条目放回正确的 System of Interest。</p></div><div class="hero-index">{''.join(nav)}</div></div><div class="hero-rule"><span>Application</span><span>System</span><span>Agent</span><span>Mechanism</span></div></header>
<main id="main">
<section class="opening"><div class="opening-copy"><p class="section-label">01 · HOW TO READ</p><h2>同一个词，可能发生在不同尺度。</h2><p>Routing 可以是 Agent 内部的一次局部分支，也可以把请求交给不同专业 Agent；Parallelization 可以是多次模型调用，也可以是多个自治单元并发工作。判断 Pattern 前，先问：此刻谁是 System of Interest？</p><div class="thesis"><strong>本文主张</strong><p>架构层级不跟随部署单元，而跟随目标所有权、自治边界、控制权、状态与协作关系。</p></div></div><figure><img src="diagrams/three-level-pattern-map.svg" alt="三层 Agentic Pattern 与实现手段地图"><figcaption>三层结构：业务责任 → 系统组织 → Agent 与局部设计；实现手段独立列出。</figcaption></figure></section>
<section class="legend-section"><div><p class="section-label">02 · VISUAL LANGUAGE</p><h2>形状表示角色，线条表示关系。</h2><p>颜色不是装饰，而是语义：Agent、Workflow、Human、Tool、Memory 和 Policy 在全文保持一致。</p></div><figure><img src="diagrams/visual-legend.svg" alt="视觉语法图例"></figure></section>
<section class="taxonomy"><p class="section-label">03 · TAXONOMY</p><h2>Pattern、机制、协议和技术，不在同一列。</h2><div class="taxonomy-grid"><div><b>Architecture Pattern</b><p>改变责任分配、控制权和系统结构。</p><small>Supervisor · Handoff · Workflow-Centric</small></div><div><b>Design Pattern</b><p>在既定边界内解决重复的局部设计问题。</p><small>Prompt Chaining · Routing · Retry</small></div><div><b>Mechanism / Protocol</b><p>提供能力或连接契约，本身不决定系统如何组织。</p><small>Memory · RAG · MCP · A2A · Skills</small></div><div><b>Technology</b><p>实现、运行或观测逻辑设计的具体产品与框架。</p><small>LangGraph · Langfuse · Agent SDK</small></div></div></section>
<section class="coverage" id="coverage"><div class="coverage-title"><p class="section-label">04 · SOURCE → LAYER</p><h2>21 个原书章节，逐项落位。</h2><p>“原资料称 Pattern”不等于“本文判定为 Architecture Pattern”。表格保留原称谓，同时给出本文分类。</p></div><div class="table-wrap"><table><thead><tr><th>Ch.</th><th>原书主题</th><th>层级</th><th>图鉴条目</th><th>本文类型</th><th>研究用 PDF</th></tr></thead><tbody>{coverage_table_html()}</tbody></table></div></section>
{''.join(sections)}
<section class="tradeoffs" id="tradeoffs"><p class="section-label">05 · ONE SLIDE ONLY</p><h2>Architecture is about trade-offs.</h2><div class="tradeoff-line"><span>Autonomy</span><span>Safety</span><span>Reliability</span><span>Latency</span><span>Cost</span><span>Observability</span><span>Maintainability</span></div><p>没有抽象意义上的“最佳 Pattern”。Pattern 选择必须回应业务重要性、技术难度、失败代价和约束条件。高自主性通常同时放大权限、安全、恢复、成本与可观测性要求。</p></section>
<section class="technology"><p class="section-label">06 · TECHNOLOGY MAPPING</p><h2>逻辑结构先行，技术映射后置。</h2><div class="mapping"><div><span>逻辑设计</span><b>Workflow Graph</b><em>→ LangGraph / Agent Framework</em></div><div><span>能力连接</span><b>Tool / Resource Boundary</b><em>→ MCP / APIs</em></div><div><span>跨 Agent</span><b>Remote Agent Contract</b><em>→ A2A</em></div><div><span>运行观察</span><b>Trace / Eval / Feedback</b><em>→ Langfuse</em></div></div><p class="technology-note">这些名称回答“如何实现与运行”，不是对架构模式的替代命名。</p></section>
<section class="references" id="references"><p class="section-label">07 · REFERENCES</p><h2>来源索引</h2><ol>{sources}</ol></section>
</main><footer class="page-footer"><p>Agentic Pattern 视觉图鉴 · 为 2 小时线上先导课与后续演示文稿准备</p><a href="#main">回到正文 ↑</a></footer></body></html>'''


CSS = r''':root{--paper:#f4f0e7;--paper-2:#fbf8f1;--ink:#172331;--muted:#5a6671;--rule:#c8c4bb;--l1:#b5472d;--l2:#1c6e67;--l3:#315ea8;--enabler:#896b24;--serif:"Iowan Old Style","Songti SC","STSong",serif;--sans:"Avenir Next","PingFang SC","Microsoft YaHei",sans-serif;color-scheme:light}*{box-sizing:border-box}html{scroll-behavior:smooth;background:var(--paper)}body{margin:0;color:var(--ink);background:var(--paper);font-family:var(--sans);font-size:clamp(16px,1.25vw,19px);line-height:1.7}.skip-link{position:absolute;left:-9999px}.skip-link:focus{left:1rem;top:1rem;background:var(--ink);color:var(--paper-2);padding:.7rem 1rem;z-index:10}a{color:inherit;text-decoration-color:color-mix(in oklab,currentColor 35%,transparent);text-underline-offset:.2em}img{display:block;max-width:100%;height:auto}.hero{min-height:92vh;padding:clamp(1.5rem,4vw,4rem);background:var(--ink);color:var(--paper-2);position:relative;overflow:hidden}.hero:after{content:"";position:absolute;right:-12vw;top:-10vw;width:48vw;height:48vw;border:1px solid #ffffff22;border-radius:50%;box-shadow:0 0 0 5vw #ffffff08,0 0 0 10vw #ffffff05;pointer-events:none}.hero-grid{display:grid;grid-template-columns:minmax(10rem,.42fr) minmax(22rem,1.2fr) minmax(18rem,.68fr);gap:clamp(2rem,5vw,6rem);min-height:72vh;align-items:end;position:relative;z-index:1}.edition{align-self:start;font-size:.72rem;letter-spacing:.22em;color:#c3cbd1;writing-mode:vertical-rl}.eyebrow,.section-label{font-size:.75rem;letter-spacing:.2em;font-weight:800;text-transform:uppercase}.hero h1{font-family:var(--serif);font-size:clamp(3.5rem,7vw,8rem);line-height:.98;letter-spacing:-.055em;margin:.4rem 0 2rem;font-weight:700}.deck{max-width:47rem;font-size:clamp(1.05rem,1.6vw,1.45rem);line-height:1.55;color:#d7dce0}.hero-index{display:grid;gap:.2rem;padding-bottom:.5rem}.hero-index a{display:grid;grid-template-columns:3rem 1fr 2rem;gap:.6rem;align-items:center;border-top:1px solid #ffffff2b;padding:.9rem 0;text-decoration:none}.hero-index b{font-family:var(--serif);font-size:1.2rem}.hero-index span{font-size:.82rem;color:#ced5d9}.hero-index em{font-style:normal;text-align:right;font-variant-numeric:tabular-nums}.hero-rule{display:grid;grid-template-columns:repeat(4,1fr);position:absolute;bottom:0;left:0;right:0;height:4.5rem}.hero-rule span{display:flex;align-items:center;padding-left:1.25rem;font-size:.74rem;letter-spacing:.08em}.hero-rule span:nth-child(1){background:var(--l1)}.hero-rule span:nth-child(2){background:var(--l2)}.hero-rule span:nth-child(3){background:var(--l3)}.hero-rule span:nth-child(4){background:var(--enabler)}main{overflow:hidden}.opening,.legend-section,.taxonomy,.coverage,.tradeoffs,.technology,.references{padding:clamp(4rem,9vw,9rem) max(5vw,calc((100vw - 1380px)/2))}.opening{display:grid;grid-template-columns:minmax(18rem,.7fr) minmax(28rem,1.3fr);gap:clamp(3rem,8vw,9rem);align-items:center}.opening h2,.legend-section h2,.taxonomy h2,.coverage h2,.tradeoffs h2,.technology h2,.references h2{font-family:var(--serif);font-size:clamp(2.5rem,5vw,5.2rem);line-height:1.04;letter-spacing:-.04em;margin:.35rem 0 1.6rem}.opening figure,.legend-section figure{margin:0}.opening figcaption,.topology figcaption{font-size:.72rem;color:var(--muted);margin-top:.7rem}.thesis{margin-top:2.5rem;padding-top:1.5rem;border-top:2px solid var(--ink)}.thesis strong{font-size:.72rem;letter-spacing:.15em;text-transform:uppercase}.legend-section{display:grid;grid-template-columns:.55fr 1.45fr;gap:5vw;background:var(--paper-2);align-items:center}.taxonomy-grid{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid var(--ink);border-bottom:1px solid var(--ink);margin-top:3rem}.taxonomy-grid>div{padding:2rem 1.4rem 2.5rem;border-right:1px solid var(--rule)}.taxonomy-grid>div:last-child{border-right:0}.taxonomy-grid b{font-family:var(--serif);font-size:1.35rem}.taxonomy-grid p{font-size:.9rem;line-height:1.55}.taxonomy-grid small{font-size:.7rem;color:var(--muted)}.coverage{background:var(--ink);color:var(--paper-2)}.coverage-title{display:grid;grid-template-columns:1fr 1fr;column-gap:5vw}.coverage-title .section-label{grid-column:1/-1}.coverage-title p:last-child{align-self:end;color:#ccd3d7}.table-wrap{overflow:auto;margin-top:3rem;border-top:1px solid #ffffff4a}table{width:100%;border-collapse:collapse;min-width:940px;font-size:.75rem}th,td{text-align:left;padding:.75rem .65rem;border-bottom:1px solid #ffffff23;vertical-align:top}th{font-size:.65rem;letter-spacing:.1em;text-transform:uppercase;color:#bec7cc}td a{color:#fff}.layer-token{font-weight:800}.layer-section{padding-bottom:clamp(5rem,12vw,12rem)}.layer-header{min-height:72vh;padding:clamp(4rem,8vw,8rem) max(5vw,calc((100vw - 1380px)/2));display:grid;grid-template-columns:.4fr 1.2fr .4fr;gap:5vw;align-items:center;color:var(--paper-2)}.l1 .layer-header{background:var(--l1)}.l2 .layer-header{background:var(--l2)}.l3 .layer-header{background:var(--l3)}.enablers .layer-header{background:var(--enabler)}.layer-number{font-family:var(--serif);font-size:clamp(5rem,12vw,13rem);line-height:1;opacity:.85}.layer-header p{font-size:.75rem;letter-spacing:.18em;text-transform:uppercase}.layer-header h2{font-family:var(--serif);font-size:clamp(3rem,6.5vw,7rem);line-height:1;margin:.5rem 0 2rem;letter-spacing:-.045em}.layer-header blockquote{font-size:clamp(1rem,1.6vw,1.4rem);margin:0;max-width:44rem}.layer-count{font-family:var(--serif);font-size:clamp(3rem,6vw,6rem);text-align:right}.layer-count small{display:block;font-family:var(--sans);font-size:.65rem;letter-spacing:.12em;text-transform:uppercase}.pattern-entry{padding:clamp(5rem,10vw,10rem) max(5vw,calc((100vw - 1280px)/2));border-bottom:1px solid var(--rule);position:relative}.pattern-entry:nth-of-type(even){background:var(--paper-2)}.pattern-kicker{display:grid;grid-template-columns:6rem 1fr 3rem;border-top:2px solid var(--ink);padding-top:.7rem;font-size:.7rem;letter-spacing:.12em;text-transform:uppercase}.pattern-kicker span:last-child{text-align:right}.pattern-heading{display:grid;grid-template-columns:.8fr 1.2fr;gap:6vw;margin:2rem 0 3rem;align-items:end}.pattern-heading h3{font-family:var(--serif);font-size:clamp(3rem,6vw,6.8rem);line-height:.96;letter-spacing:-.055em;margin:0}.english-name{font-size:.85rem;color:var(--muted);letter-spacing:.04em}.intent{font-family:var(--serif);font-size:clamp(1.4rem,2.4vw,2.25rem);line-height:1.45;margin:0}.topology{margin:0}.topology a{display:block;border:1px solid var(--rule);background:var(--paper-2)}.pattern-notes{display:grid;grid-template-columns:repeat(3,1fr);gap:3vw;margin:3rem 0}.pattern-notes section{border-top:3px solid var(--ink);padding-top:1rem}.pattern-notes h4{font-size:.7rem;letter-spacing:.14em;text-transform:uppercase;margin:0}.pattern-notes p{font-size:.9rem;line-height:1.6}.boundary-note{display:grid;grid-template-columns:.7fr 1.1fr 1.2fr;border-top:1px solid var(--rule);border-bottom:1px solid var(--rule)}.boundary-note>div{padding:1.3rem;border-right:1px solid var(--rule)}.boundary-note>div:last-child{border-right:0}.boundary-note span{font-size:.65rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}.boundary-note p{font-size:.78rem;line-height:1.55;margin:.4rem 0}.technique-strip{display:flex;flex-wrap:wrap;gap:.55rem;margin:2rem 0}.technique-strip span{border:1px solid var(--rule);padding:.45rem .7rem;font-size:.7rem;background:var(--paper-2)}.pattern-sources{display:grid;grid-template-columns:5rem 1fr;gap:.55rem 1rem;margin-top:2rem;font-size:.7rem}.pattern-sources>span{letter-spacing:.14em;text-transform:uppercase}.pattern-sources a{grid-column:2;display:flex;gap:.65rem;text-decoration:none}.pattern-sources a span{font-weight:800;min-width:10rem}.tradeoffs{background:#e5dfd2}.tradeoff-line{display:flex;flex-wrap:wrap;gap:.6rem;margin:3rem 0}.tradeoff-line span{border:1px solid var(--ink);padding:.65rem 1rem;font-size:.78rem}.tradeoffs>p:last-child{max-width:70rem;font-family:var(--serif);font-size:clamp(1.2rem,2.1vw,1.8rem)}.technology{background:var(--paper-2)}.mapping{display:grid;grid-template-columns:repeat(4,1fr);border-top:2px solid var(--ink);margin-top:3rem}.mapping>div{padding:1.5rem;border-right:1px solid var(--rule)}.mapping>div:last-child{border:0}.mapping span,.mapping em{display:block;font-size:.7rem;color:var(--muted);font-style:normal}.mapping b{display:block;font-family:var(--serif);font-size:1.2rem;margin:.6rem 0}.technology-note{margin-top:2rem;font-weight:700}.references ol{list-style:none;padding:0;display:grid;grid-template-columns:repeat(2,1fr);gap:0 4vw}.references li{display:grid;grid-template-columns:7rem 1fr;padding:1rem 0;border-top:1px solid var(--rule)}.references li>span{font-size:.65rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}.references li>a{font-weight:750}.references li p{grid-column:2;font-size:.72rem;color:var(--muted);margin:.25rem 0}.page-footer{padding:2rem 5vw;background:var(--ink);color:var(--paper-2);display:flex;justify-content:space-between;font-size:.72rem}@media(max-width:900px){.hero-grid{grid-template-columns:1fr;align-items:start;padding-bottom:7rem}.edition{writing-mode:horizontal-tb}.hero-index{margin-top:2rem}.opening,.legend-section,.coverage-title{grid-template-columns:1fr}.taxonomy-grid,.mapping{grid-template-columns:repeat(2,1fr)}.layer-header{grid-template-columns:1fr}.layer-number{font-size:6rem}.layer-count{text-align:left}.pattern-heading{grid-template-columns:1fr}.pattern-notes{grid-template-columns:1fr}.boundary-note{grid-template-columns:1fr}.boundary-note>div{border-right:0;border-bottom:1px solid var(--rule)}.references ol{grid-template-columns:1fr}}@media(max-width:560px){.hero{padding:1.25rem}.hero h1{font-size:3.3rem}.hero-rule span{font-size:.7rem;padding-left:.4rem}.opening,.legend-section,.taxonomy,.coverage,.tradeoffs,.technology,.references,.pattern-entry,.layer-header{padding-left:1.2rem;padding-right:1.2rem}.taxonomy-grid,.mapping{grid-template-columns:1fr}.taxonomy-grid>div,.mapping>div{border-right:0;border-bottom:1px solid var(--rule)}.pattern-kicker{grid-template-columns:3rem 1fr 2rem}.pattern-heading h3{font-size:3rem}.boundary-note{display:block}.pattern-sources{grid-template-columns:1fr}.pattern-sources a,.pattern-sources>span{grid-column:1}.pattern-sources a{display:block}.pattern-sources a span{display:block}.references li{grid-template-columns:1fr}.references li p{grid-column:1}.page-footer{display:block}}@media print{.hero{min-height:auto;break-after:page}.hero-grid{min-height:auto}.hero:after,.skip-link{display:none}.layer-header{min-height:auto;break-before:page;break-after:page}.pattern-entry{break-before:page;padding-top:2cm;padding-bottom:1.5cm}.topology a{border:0}.topology figcaption{display:none}.opening,.legend-section,.taxonomy,.coverage,.tradeoffs,.technology,.references{break-before:page}.page-footer{display:none}a{text-decoration:none}.pattern-entry:nth-of-type(even){background:var(--paper)}}'''


ATLAS_JS = r'''(() => {
  const init = () => {
    const root = document.querySelector('[data-atlas-browser]');
    if (!root) return;
    document.documentElement.classList.add('has-js');
    const input = root.querySelector('[data-pattern-search]');
    const filters = [...root.querySelectorAll('[data-layer-filter]')];
    const entries = [...document.querySelectorAll('.pattern-entry')];
    const layers = [...document.querySelectorAll('.layer-section')];
    const compoundDividers = [...document.querySelectorAll('.compound-divider')];
    const status = root.querySelector('[data-filter-status]');
    const directory = document.querySelector('.atlas-directory');
    const legend = document.querySelector('.legend-section');
    const l1RelativeMap = document.querySelector('.l1-relative-map');
    let layer = 'ALL';

    const normalize = value => value.toLocaleLowerCase('zh-Hans').trim();
    const apply = () => {
      const query = normalize(input.value);
      let visible = 0;
      entries.forEach(entry => {
        const matchesLayer = layer === 'ALL' || entry.dataset.layer === layer;
        const matchesQuery = !query || normalize(entry.dataset.search || '').includes(query);
        entry.hidden = !(matchesLayer && matchesQuery);
        if (!entry.hidden) visible += 1;
      });
      layers.forEach(section => {
        section.hidden = !section.querySelector('.pattern-entry:not([hidden])');
      });
      compoundDividers.forEach(divider => {
        const visibleCompound = document.querySelector(`.pattern-entry[data-layer="${divider.dataset.layer}"][data-organization="compound"]:not([hidden])`);
        divider.hidden = !visibleCompound;
      });
      const filtering = layer !== 'ALL' || Boolean(query);
      if (directory) directory.hidden = filtering;
      if (legend) legend.hidden = filtering;
      if (l1RelativeMap) l1RelativeMap.hidden = Boolean(query) || (layer !== 'ALL' && layer !== 'L1');
      document.body.classList.toggle('atlas-filtering', filtering);
      status.textContent = `显示 ${visible} / ${entries.length} 个条目`;
    };

    input.addEventListener('input', apply);
    filters.forEach(button => button.addEventListener('click', () => {
      layer = button.dataset.layerFilter;
      filters.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
      apply();
    }));
    apply();
  };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();'''


TAXONOMY_JS = r'''(() => {
  const init = () => {
    const root = document.querySelector('[data-taxonomy-browser]');
    if (!root) return;
    const input = root.querySelector('[data-taxonomy-search]');
    const select = root.querySelector('[data-taxonomy-select]');
    const filters = [...root.querySelectorAll('[data-taxonomy-layer]')];
    const groups = [...document.querySelectorAll('.taxonomy-group')];
    const entries = [...document.querySelectorAll('.taxonomy-pattern')];
    const status = root.querySelector('[data-taxonomy-status]');
    let layer = 'ALL';

    const requestedGroup = new URLSearchParams(window.location.search).get('group');
    if (requestedGroup && [...select.options].some(option => option.value === requestedGroup)) {
      select.value = requestedGroup;
    }

    const normalize = value => value.toLocaleLowerCase('zh-Hans').trim();
    const apply = () => {
      const query = normalize(input.value);
      const taxonomy = select.value;
      let visible = 0;
      entries.forEach(entry => {
        const matchesLayer = layer === 'ALL' || entry.dataset.layer === layer;
        const matchesTaxonomy = taxonomy === 'ALL' || entry.dataset.taxonomy === taxonomy;
        const matchesQuery = !query || normalize(entry.dataset.search || '').includes(query);
        entry.hidden = !(matchesLayer && matchesTaxonomy && matchesQuery);
        if (!entry.hidden) visible += 1;
      });
      groups.forEach(group => {
        group.hidden = !group.querySelector('.taxonomy-pattern:not([hidden])');
      });
      status.textContent = `显示 ${visible} / ${entries.length} 个条目`;
    };

    input.addEventListener('input', apply);
    select.addEventListener('change', apply);
    filters.forEach(button => button.addEventListener('click', () => {
      layer = button.dataset.taxonomyLayer;
      filters.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
      apply();
    }));
    apply();
  };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();'''


CSS += r'''
:focus-visible{outline:3px solid #d88b43;outline-offset:4px}.visually-hidden{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;overflow:hidden!important;clip:rect(0,0,0,0)!important;white-space:nowrap!important;border:0!important}.site-nav{position:sticky;top:0;z-index:20;display:flex;align-items:center;justify-content:space-between;gap:2rem;min-height:4rem;padding:.65rem max(5vw,calc((100vw - 1380px)/2));background:color-mix(in oklab,var(--ink) 96%,transparent);color:var(--paper-2);border-bottom:1px solid #ffffff26;backdrop-filter:saturate(110%) blur(8px)}.site-mark{font-family:var(--serif);font-size:1.1rem;font-weight:800;letter-spacing:-.03em;text-decoration:none}.site-links{display:flex;gap:1.3rem;align-items:center;font-size:.75rem}.site-links a{text-decoration:none;color:#cbd3d7}.site-links a[aria-current=page]{color:var(--paper-2);text-decoration:underline;text-decoration-thickness:2px}.article-meta{display:flex;flex-wrap:wrap;gap:.55rem 1.2rem;margin-top:1.8rem;font-size:.72rem;color:#c5ced3}.article-meta span+span:before{content:"·";margin-right:1.2rem;color:#6f7c84}.hero-actions{display:flex;flex-wrap:wrap;gap:.75rem;margin-top:2rem}.hero-actions a{border:1px solid #ffffff55;padding:.65rem 1rem;text-decoration:none;font-size:.76rem;font-weight:750}.hero-actions a:first-child{background:var(--paper-2);color:var(--ink)}.reading-paths,.content-section,.case-section,.anchor-section,.comparisons,.decision-section,.conclusion-section,.method-section,.atlas-directory,.atlas-tools-wrap{padding:clamp(4rem,9vw,9rem) max(5vw,calc((100vw - 1380px)/2))}.reading-paths{background:var(--paper-2);display:grid;grid-template-columns:.55fr repeat(3,1fr);gap:0;border-bottom:1px solid var(--rule)}.reading-paths>header{padding-right:3vw}.reading-paths h2{font-family:var(--serif);font-size:clamp(2rem,3.5vw,3.5rem);line-height:1.05;margin:.25rem 0}.reading-path{display:block;padding:1rem 1.3rem 1.3rem;border-top:2px solid var(--ink);text-decoration:none}.reading-path+.reading-path{margin-left:1.5rem}.reading-path strong{display:block;font-family:var(--serif);font-size:1.15rem}.reading-path span{display:block;margin-top:.55rem;color:var(--muted);font-size:.75rem;line-height:1.5}.chapter-mark{display:grid;grid-template-columns:minmax(4rem,.28fr) minmax(18rem,1fr);gap:clamp(1rem,4vw,4rem);align-items:start;margin-bottom:clamp(2.5rem,5vw,5rem)}.chapter-mark>span{font-family:var(--serif);font-size:clamp(3.5rem,8vw,8rem);line-height:.8;color:color-mix(in oklab,var(--ink) 24%,transparent)}.chapter-mark h2{font-family:var(--serif);font-size:clamp(2.5rem,5vw,5.2rem);line-height:1.04;letter-spacing:-.04em;margin:0}.chapter-mark p{max-width:65ch;color:var(--muted)}.problem-section{background:#e5dfd2}.problem-grid{display:grid;grid-template-columns:minmax(17rem,.7fr) minmax(28rem,1.3fr);gap:clamp(3rem,8vw,8rem);align-items:start}.impossible-question{font-family:var(--serif);font-size:clamp(1.9rem,3.3vw,3.4rem);line-height:1.26;margin:0}.wrong-choice{border:1px solid var(--ink);padding:clamp(1.3rem,3vw,2.6rem);background:var(--paper-2)}.wrong-choice b{display:block;font-size:.72rem;letter-spacing:.12em;text-transform:uppercase}.wrong-choice p{font-size:1.08rem}.four-answers{display:grid;grid-template-columns:repeat(2,1fr);border-top:1px solid var(--rule);border-bottom:1px solid var(--rule)}.four-answers div{padding:1rem;border-right:1px solid var(--rule)}.four-answers div:nth-child(2n){border-right:0}.four-answers div:nth-child(-n+2){border-bottom:1px solid var(--rule)}.four-answers strong{display:block;font-family:var(--serif);font-size:1.1rem}.four-answers span{font-size:.74rem;color:var(--muted)}.thesis-list{margin:3rem 0 0;padding:0;list-style:none;counter-reset:claims}.thesis-list li{counter-increment:claims;display:grid;grid-template-columns:3rem 1fr;gap:1rem;padding:1rem 0;border-top:1px solid var(--rule)}.thesis-list li:before{content:counter(claims,decimal-leading-zero);font-family:var(--serif);font-weight:800}.map-section{background:var(--paper)}.map-layout{display:grid;grid-template-columns:minmax(18rem,.62fr) minmax(32rem,1.38fr);gap:clamp(3rem,7vw,7rem);align-items:center}.map-layout figure{margin:0}.map-layout figcaption,.case-figure figcaption{font-size:.76rem;color:var(--muted);margin-top:.75rem}.diagnostic-questions{display:grid;border-top:2px solid var(--ink);margin-top:2rem}.diagnostic-questions div{display:grid;grid-template-columns:3rem 1fr;padding:.8rem 0;border-bottom:1px solid var(--rule)}.diagnostic-questions b{font-family:var(--serif)}.case-section{background:var(--ink);color:var(--paper-2)}.case-section .chapter-mark>span{color:#ffffff35}.case-section .chapter-mark p{color:#c8d0d4}.case-brief{max-width:70ch;font-family:var(--serif);font-size:clamp(1.25rem,2.1vw,1.85rem);line-height:1.55}.case-figure{margin:3rem 0}.case-figure img{background:var(--paper-2)}.case-grid{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid #ffffff55;border-bottom:1px solid #ffffff55}.case-grid article{padding:1.3rem;border-right:1px solid #ffffff30}.case-grid article:last-child{border-right:0}.case-grid b{font-family:var(--serif);font-size:1.5rem}.case-grid small{display:block;color:#bdc7cc}.case-grid strong{display:block;margin:.65rem 0}.case-grid p{font-size:.78rem;line-height:1.55;color:#d6dcdf}.case-conclusion{max-width:70ch;margin:2.5rem 0 0;font-family:var(--serif);font-size:clamp(1.25rem,2vw,1.75rem)}.anchor-section{background:var(--paper-2)}.anchor-index{list-style:none;padding:0;margin:0;border-top:2px solid var(--ink)}.anchor-index li{border-bottom:1px solid var(--rule)}.anchor-index a{display:grid;grid-template-columns:4rem minmax(12rem,.65fr) minmax(18rem,1.35fr) 7rem;gap:1rem;align-items:baseline;padding:1rem 0;text-decoration:none}.anchor-index .anchor-layer{font-family:var(--serif);font-weight:800}.anchor-index strong{font-family:var(--serif);font-size:1.15rem}.anchor-index p{margin:0;font-size:.8rem;color:var(--muted)}.anchor-index em{font-style:normal;font-size:.68rem;text-align:right}.comparisons{background:var(--paper)}.comparison-block{padding:clamp(3rem,6vw,6rem) 0;border-top:1px solid var(--ink)}.comparison-block header{display:grid;grid-template-columns:.75fr 1.25fr;gap:5vw;margin-bottom:2rem}.comparison-block h3{font-family:var(--serif);font-size:clamp(2rem,4vw,4rem);line-height:1.05;margin:0}.comparison-block header p{max-width:60ch;margin:0}.comparison-wrap{overflow:auto;border-top:2px solid var(--ink)}.comparison-table{min-width:760px;color:var(--ink);font-size:.74rem}.comparison-table th{color:var(--muted);border-bottom:1px solid var(--ink);background:#e9e4da}.comparison-table td{border-bottom:1px solid var(--rule)}.comparison-summary{max-width:68ch;margin:1.3rem 0 0;font-family:var(--serif);font-size:1.15rem;font-weight:700}.decision-section{background:#e5dfd2}.decision-grid{border-top:2px solid var(--ink)}.decision-grid article{display:grid;grid-template-columns:4rem minmax(16rem,.75fr) minmax(20rem,1.25fr);gap:2rem;padding:1.4rem 0;border-bottom:1px solid var(--rule)}.decision-grid b{font-family:var(--serif);font-size:1.5rem}.decision-grid h3{font-family:var(--serif);font-size:1.25rem;margin:0}.decision-grid p{margin:0;font-size:.86rem}.default-rule{margin:3rem 0 0;max-width:68ch;font-family:var(--serif);font-size:clamp(1.35rem,2.4vw,2.1rem);line-height:1.45}.conclusion-section{background:var(--ink);color:var(--paper-2)}.conclusion-section .chapter-mark>span{color:#ffffff35}.conclusion-copy{max-width:75ch}.conclusion-copy p{font-family:var(--serif);font-size:clamp(1.2rem,2vw,1.7rem);line-height:1.6}.atlas-cta{display:grid;grid-template-columns:1fr auto;gap:2rem;align-items:center;margin-top:3rem;padding-top:2rem;border-top:1px solid #ffffff55}.atlas-cta a{display:inline-block;padding:.8rem 1.1rem;background:var(--paper-2);color:var(--ink);text-decoration:none;font-weight:800}.method-section{background:var(--paper-2)}.method-grid{display:grid;grid-template-columns:repeat(4,1fr);border-top:2px solid var(--ink);border-bottom:1px solid var(--ink)}.method-grid article{padding:1.3rem;border-right:1px solid var(--rule)}.method-grid article:last-child{border-right:0}.method-grid b{font-family:var(--serif);font-size:1.1rem}.method-grid p{font-size:.76rem;line-height:1.55}.citation-box{display:grid;grid-template-columns:.55fr 1.45fr;gap:3rem;margin-top:3rem}.citation-box code{display:block;white-space:normal;background:#e9e4da;padding:1rem;font-family:var(--sans);font-size:.75rem}.compact-references{margin-top:4rem}.compact-references h3{font-family:var(--serif);font-size:2rem}.compact-references ol{list-style:none;padding:0;display:grid;grid-template-columns:repeat(2,1fr);gap:0 4vw}.compact-references li{padding:.85rem 0;border-top:1px solid var(--rule);font-size:.75rem}.compact-references li span{display:block;color:var(--muted)}.atlas-hero{padding:clamp(3rem,7vw,7rem) max(5vw,calc((100vw - 1380px)/2));background:var(--ink);color:var(--paper-2)}.atlas-hero-grid{display:grid;grid-template-columns:1.15fr .85fr;gap:7vw;align-items:end}.atlas-hero h1{font-family:var(--serif);font-size:clamp(3.5rem,7vw,7rem);line-height:.98;letter-spacing:-.05em;margin:.5rem 0 1.5rem}.atlas-hero p{max-width:62ch;color:#d2d9dc}.atlas-hero-meta{display:grid;border-top:1px solid #ffffff55}.atlas-hero-meta span{display:flex;justify-content:space-between;padding:.65rem 0;border-bottom:1px solid #ffffff25;font-size:.75rem}.atlas-tools-wrap{padding-top:2rem;padding-bottom:2rem;background:var(--paper-2);position:sticky;top:4rem;z-index:10;border-bottom:1px solid var(--rule)}.atlas-tools{display:grid;grid-template-columns:minmax(14rem,1fr) auto auto;gap:1rem;align-items:center}.atlas-tools label{font-size:.72rem;font-weight:800}.atlas-tools input{width:100%;padding:.75rem .9rem;border:1px solid var(--ink);background:var(--paper);color:var(--ink);font:inherit;font-size:.84rem}.layer-filters{display:flex;gap:.35rem}.layer-filters button{border:1px solid var(--rule);background:transparent;color:var(--ink);padding:.55rem .7rem;font:inherit;font-size:.7rem;cursor:pointer}.layer-filters button[aria-pressed=true]{background:var(--ink);color:var(--paper-2);border-color:var(--ink)}.filter-status{font-size:.72rem;color:var(--muted);min-width:9rem;text-align:right}.atlas-directory{padding-top:4rem;padding-bottom:4rem}.directory-grid{display:grid;grid-template-columns:repeat(4,1fr);border-top:2px solid var(--ink)}.directory-column{padding:1.2rem;border-right:1px solid var(--rule)}.directory-column:last-child{border-right:0}.directory-column h2{font-family:var(--serif);font-size:1.4rem;margin:.2rem 0 1rem}.directory-column ol{list-style:none;padding:0;margin:0}.directory-column li{padding:.42rem 0;border-top:1px solid color-mix(in oklab,var(--rule) 60%,transparent);font-size:.7rem}.directory-column a{text-decoration:none}.atlas-page .layer-header{min-height:46vh}.atlas-page .pattern-entry{content-visibility:auto;contain-intrinsic-size:1900px;padding-top:clamp(4rem,8vw,8rem);padding-bottom:clamp(4rem,8vw,8rem)}.atlas-page .pattern-heading h3{font-size:clamp(2.8rem,5vw,5.3rem)}.pattern-kicker{grid-template-columns:5rem minmax(8rem,1fr) 7rem 3rem}.pattern-kicker .provenance{font-weight:850;color:var(--muted)}.structure-notes{display:grid;grid-template-columns:repeat(2,1fr);border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);margin:2rem 0}.structure-notes section{padding:1.2rem;border-right:1px solid var(--rule);border-bottom:1px solid var(--rule)}.structure-notes section:nth-child(2n){border-right:0}.structure-notes section:nth-last-child(-n+2){border-bottom:0}.structure-notes h4{font-size:.68rem;letter-spacing:.1em;text-transform:uppercase;margin:0}.structure-notes p{font-size:.8rem;line-height:1.6;margin:.45rem 0}.example-note{display:grid;grid-template-columns:7rem 1fr;gap:1rem;padding:1.15rem 0;border-top:2px solid var(--ink);margin:2rem 0}.example-note strong{font-size:.68rem;letter-spacing:.1em;text-transform:uppercase}.example-note p{margin:0;font-family:var(--serif);font-size:1.1rem}.pattern-sources a:after,.compact-references a:after,.references a:after{content:" ↗"}.publication-note{padding:1rem max(5vw,calc((100vw - 1380px)/2));background:#e5dfd2;font-size:.7rem;color:var(--muted)}[hidden]{display:none!important}@media(max-width:1000px){.reading-paths{grid-template-columns:1fr}.reading-path+.reading-path{margin-left:0}.reading-paths>header{margin-bottom:2rem}.case-grid,.method-grid,.directory-grid{grid-template-columns:repeat(2,1fr)}.case-grid article:nth-child(2){border-right:0}.case-grid article:nth-child(-n+2){border-bottom:1px solid #ffffff30}.method-grid article:nth-child(2){border-right:0}.method-grid article:nth-child(-n+2){border-bottom:1px solid var(--rule)}.directory-column:nth-child(2){border-right:0}.directory-column:nth-child(-n+2){border-bottom:1px solid var(--rule)}.atlas-tools{grid-template-columns:1fr}.filter-status{text-align:left}.atlas-hero-grid{grid-template-columns:1fr}}@media(max-width:760px){.site-nav{position:static;align-items:flex-start}.site-links{flex-wrap:wrap;justify-content:flex-end}.problem-grid,.map-layout,.comparison-block header,.citation-box{grid-template-columns:1fr}.chapter-mark{grid-template-columns:1fr}.chapter-mark>span{font-size:4rem}.anchor-index a{grid-template-columns:3rem 1fr}.anchor-index p,.anchor-index em{grid-column:2}.decision-grid article{grid-template-columns:3rem 1fr}.decision-grid p{grid-column:2}.atlas-cta{grid-template-columns:1fr}.compact-references ol{grid-template-columns:1fr}.atlas-tools-wrap{position:static}.pattern-kicker{grid-template-columns:3rem 1fr 6rem 2rem}.structure-notes{grid-template-columns:1fr}.structure-notes section{border-right:0}.structure-notes section:nth-last-child(-n+2){border-bottom:1px solid var(--rule)}.structure-notes section:last-child{border-bottom:0}}@media(max-width:560px){.site-nav{padding:.7rem 1.2rem}.site-links{gap:.65rem;font-size:.68rem}.reading-paths,.content-section,.case-section,.anchor-section,.comparisons,.decision-section,.conclusion-section,.method-section,.atlas-directory,.atlas-tools-wrap,.atlas-hero{padding-left:1.2rem;padding-right:1.2rem}.four-answers,.case-grid,.method-grid,.directory-grid{grid-template-columns:1fr}.four-answers div,.case-grid article,.method-grid article,.directory-column{border-right:0!important;border-bottom:1px solid var(--rule)}.four-answers div:last-child,.case-grid article:last-child,.method-grid article:last-child,.directory-column:last-child{border-bottom:0}.layer-filters{flex-wrap:wrap}.pattern-kicker{grid-template-columns:2.5rem 1fr 5.5rem 2rem;font-size:.62rem}.example-note{grid-template-columns:1fr}.article-meta span+span:before{content:"";margin:0}}@media print{.site-nav,.atlas-tools-wrap,.reading-paths,.hero-actions{display:none!important}.content-section,.case-section,.anchor-section,.comparisons,.decision-section,.conclusion-section,.method-section,.atlas-directory{break-before:page}.comparison-block{break-inside:avoid}.pattern-entry[hidden],.layer-section[hidden]{display:block!important}.pattern-entry{content-visibility:visible!important;contain:none!important}.article-meta{color:var(--paper-2)}}
'''


CSS += r'''
html{overflow-wrap:anywhere}main{overflow:visible}.topology>a,.diagram-viewport{display:block;overflow-x:auto;overscroll-behavior-inline:contain;scrollbar-gutter:stable;border:1px solid var(--rule);background:var(--paper-2)}.topology>a>img,.diagram-viewport>img,.topology>a>.inline-svg,.diagram-viewport>.inline-svg{width:100%;min-width:0}.topology>a:focus-visible,.diagram-viewport:focus-visible{outline:3px solid #d88b43;outline-offset:3px}.topology a{border:1px solid var(--rule)}.standalone-alt{display:none!important}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}@media(max-width:900px){.problem-grid,.map-layout,.comparison-block header,.citation-box{grid-template-columns:1fr}}@media(max-width:1100px){.topology figcaption{font-size:.78rem}.topology figcaption:after{content:" 窄屏可横向滑动查看细节。"}.topology>a>img,.diagram-viewport>img,.topology>a>.inline-svg,.diagram-viewport>.inline-svg{min-width:1040px}.pattern-sources,.boundary-note p,.directory-column li,.filter-status{font-size:.75rem}}@page{size:A4 portrait;margin:12mm}@media print{html,body,main{overflow:visible!important;background:var(--paper-2)!important;color:var(--ink)!important}body{font-size:10pt}.hero,.atlas-hero,.case-section,.conclusion-section,.coverage,.layer-header{background:var(--paper-2)!important;color:var(--ink)!important;border:1px solid var(--rule)}.hero *,.atlas-hero *,.case-section *,.conclusion-section *,.coverage *,.layer-header *{color:var(--ink)!important}.hero-rule{display:none!important}.hero,.atlas-hero{break-after:page}.hero-grid{display:block!important}.hero-index{margin-top:2cm}.case-grid{border-color:var(--ink)}.case-grid article{border-color:var(--rule)}.table-wrap,.comparison-wrap,.topology>a,.diagram-viewport{overflow:visible!important}.coverage table,.comparison-table{min-width:0!important;width:100%!important;table-layout:fixed;font-size:6.5pt}.coverage th,.coverage td,.comparison-table th,.comparison-table td{padding:3pt!important;border-color:var(--rule)!important;color:var(--ink)!important;word-break:break-word}.coverage th,.comparison-table th{background:var(--paper)!important}.topology>a>img,.diagram-viewport>img,.topology>a>.inline-svg,.diagram-viewport>.inline-svg{min-width:0!important;width:100%!important}.topology,.pattern-heading,.pattern-notes,.structure-notes,.example-note{break-inside:avoid}.pattern-entry{break-before:page;widows:3;orphans:3}.topology figcaption{display:block!important}.topology figcaption:after{content:""}.publication-note{background:var(--paper-2);color:var(--ink)}a{color:var(--ink)!important}}
'''


CSS += r'''
.site-mark{flex:0 0 auto;white-space:nowrap;position:relative;z-index:2}.site-links{min-width:0;position:relative;z-index:1}.site-links a{white-space:nowrap}.hero h1 small{display:block;margin-top:1.2rem;font-family:var(--sans);font-size:.16em;line-height:1.45;letter-spacing:.09em;text-transform:uppercase}.skip-to-conclusion{display:inline-block;margin-top:2rem;padding:.75rem 1rem;border:1px solid #ffffff55;text-decoration:none;font-size:.76rem;font-weight:800}.comparison-table th:first-child,.comparison-table td:first-child{position:sticky;left:0;z-index:1;background:var(--paper)}.comparison-table th:first-child{z-index:2;background:#e9e4da}.pattern-entry{scroll-margin-top:8rem}.atlas-filtering .layer-header{min-height:auto;padding-top:1.25rem;padding-bottom:1.25rem;grid-template-columns:auto 1fr auto}.atlas-filtering .layer-number,.atlas-filtering .layer-count{font-size:1.7rem}.atlas-filtering .layer-header h2{font-size:1.6rem;margin:0}.atlas-filtering .layer-header p,.atlas-filtering .layer-header blockquote,.atlas-filtering .layer-count small{display:none}
@media(max-width:1100px){.diagram-viewport>figcaption:after{content:" 窄屏可横向滑动查看完整关系。"}.comparison-wrap:before{content:"← 横向滑动查看完整比较 →";display:block;padding:.45rem .6rem;color:var(--muted);font-size:.72rem;background:var(--paper-2)}}
@media(max-width:760px){.comparison-block{display:flex;flex-direction:column}.comparison-block header{order:0}.comparison-summary{order:1;margin-bottom:1rem}.comparison-wrap{order:2}}
@media(max-width:560px){.site-nav{display:grid;grid-template-columns:1fr;gap:.45rem;backdrop-filter:none}.site-links{justify-content:flex-start!important;gap:1rem}}
@media print{.atlas-directory[hidden],.legend-section[hidden]{display:block!important}.comparison-wrap:before,.diagram-viewport>figcaption:after{content:""}.comparison-table th:first-child,.comparison-table td:first-child{position:static}.skip-to-conclusion{display:none!important}}
'''


CSS += r'''
.case-study{margin:clamp(2.5rem,5vw,4.5rem) 0 2.5rem;padding:clamp(1.4rem,3vw,2.5rem);background:#e9e4da;border-top:2px solid var(--ink);border-bottom:1px solid var(--ink)}.case-study-header{display:grid;grid-template-columns:minmax(18rem,1fr) auto;gap:2rem;align-items:end;padding-bottom:1.2rem;border-bottom:1px solid var(--rule)}.case-kind{margin:0 0 .4rem;font-size:.66rem;line-height:1.2;letter-spacing:.14em;font-weight:850;text-transform:uppercase;color:var(--muted)}.case-study h4{margin:0;font-family:var(--serif);font-size:clamp(1.7rem,3vw,2.8rem);line-height:1.1}.case-project{margin:0;font-size:.78rem;font-weight:850;text-align:right}.case-study-body{display:grid;grid-template-columns:repeat(3,1fr)}.case-study-body section{padding:1.3rem 1.3rem 1.3rem 0}.case-study-body section+section{padding-left:1.3rem;border-left:1px solid var(--rule)}.case-study-body h5{margin:0 0 .55rem;font-size:.66rem;letter-spacing:.1em;text-transform:uppercase}.case-study-body p{max-width:70ch;margin:0;font-size:.8rem;line-height:1.65}.case-references{display:flex;flex-wrap:wrap;gap:.45rem 1rem;padding-top:1rem;border-top:1px solid var(--rule);font-size:.7rem}.case-references span{font-weight:850;letter-spacing:.1em;text-transform:uppercase}.case-references a{font-weight:700}.pattern-sources{margin-top:1.5rem}
@media(max-width:820px){.case-study-header{grid-template-columns:1fr}.case-project{text-align:left}.case-study-body{grid-template-columns:1fr}.case-study-body section{padding:1rem 0}.case-study-body section+section{padding-left:0;border-left:0;border-top:1px solid var(--rule)}}
@media print{.case-study{background:var(--paper)!important;break-inside:auto}.case-study-header,.case-study-body section,.case-references{break-inside:avoid}.case-study-body{grid-template-columns:1fr}.case-study-body section{padding:.7rem 0}.case-study-body section+section{padding-left:0;border-left:0;border-top:1px solid var(--rule)}}
'''

CSS += r'''
.l1-relative-map{min-height:92vh;padding:clamp(4rem,8vw,8rem) max(5vw,calc((100vw - 1380px)/2));display:grid;grid-template-columns:minmax(15rem,.48fr) minmax(32rem,1.52fr);gap:clamp(2.5rem,6vw,6rem);align-items:center;background:#e9e4da;border-top:1px solid var(--ink);border-bottom:1px solid var(--ink)}.l1-relative-copy .section-label{color:var(--l1)}.l1-relative-copy h3{margin:.35rem 0 1.4rem;font-family:var(--serif);font-size:clamp(2.5rem,5vw,5rem);line-height:1.03;letter-spacing:-.045em}.l1-relative-copy>p:not(.section-label){max-width:52ch;font-size:.88rem;line-height:1.65}.l1-relative-axes{margin:2rem 0 0;padding:0;list-style:none;border-top:2px solid var(--ink)}.l1-relative-axes li{padding:.8rem 0;border-bottom:1px solid var(--rule);font-size:.74rem;line-height:1.5}.l1-relative-axes b{display:block;font-size:.66rem;letter-spacing:.1em;text-transform:uppercase}.l1-relative-figure{margin:0;min-width:0}.l1-relative-figure>a{display:block;overflow-x:auto;overscroll-behavior-inline:contain;scrollbar-gutter:stable;border:1px solid var(--rule);background:var(--paper-2)}.l1-relative-figure>a>img{width:100%;min-width:0}.l1-relative-figure figcaption{margin-top:.8rem;color:var(--muted);font-size:.72rem;line-height:1.55}
@media(max-width:900px){.l1-relative-map{min-height:auto;grid-template-columns:1fr}.l1-relative-copy>p:not(.section-label){max-width:70ch}}
@media(max-width:1100px){.l1-relative-figure>a>img{min-width:1040px}}
@media(max-width:560px){.l1-relative-map{padding-left:1.2rem;padding-right:1.2rem}.l1-relative-copy h3{font-size:2.7rem}}
@media print{.l1-relative-map{display:grid!important;min-height:0;break-before:page;break-after:page;padding:1cm 0;background:var(--paper-2)!important;grid-template-columns:1fr}.l1-relative-map[hidden]{display:grid!important}.l1-relative-copy h3{font-size:28pt}.l1-relative-axes{display:none}.l1-relative-figure{break-inside:avoid}.l1-relative-figure>a>img{min-width:0!important;width:100%!important}}
'''

CSS += r'''
.directory-pattern>a{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:.55rem;align-items:baseline}.directory-role{font-size:.55rem;letter-spacing:.09em;font-weight:850;color:var(--muted)}.directory-variants{margin:.35rem 0 .25rem .4rem!important;padding-left:.8rem!important;border-left:1px solid var(--ink)}.directory-column .directory-variants li{border-top:0;padding:.24rem 0}.directory-variants a{display:grid;grid-template-columns:3.7rem minmax(0,1fr);gap:.35rem;color:var(--muted)}.directory-variants a span{font-size:.52rem;letter-spacing:.08em;font-weight:850;color:var(--ink)}.directory-compounds{margin-top:1.4rem;padding-top:1rem;border-top:2px solid var(--ink)}.directory-compounds h3{margin:0 0 .35rem;font-size:.58rem;letter-spacing:.12em}.directory-compounds li{font-weight:750}.directory-l2 .directory-compounds h3{color:var(--l2)}.directory-l3 .directory-compounds h3{color:var(--enabler)}
.pattern-lineage{display:grid;grid-template-columns:minmax(9rem,.32fr) minmax(18rem,1.68fr);gap:2rem;align-items:start;margin:1.6rem 0 0;padding:1rem 0;border-top:1px solid var(--ink);border-bottom:1px solid var(--rule)}.pattern-lineage>span,.pattern-lineage b{font-size:.62rem;line-height:1.45;letter-spacing:.12em;font-weight:850;text-transform:uppercase}.pattern-lineage>div{display:flex;flex-wrap:wrap;gap:.35rem 1rem;align-items:baseline}.pattern-lineage>div b{width:100%;color:var(--muted)}.pattern-lineage a{font-family:var(--serif);font-size:.9rem;font-weight:750}.pattern-lineage p{flex-basis:100%;max-width:76ch;margin:.35rem 0 0;color:var(--muted);font-size:.72rem;line-height:1.55}.lineage-common>span{color:var(--ink)}.lineage-variant{padding-left:1rem;border-left:1px solid var(--ink)}.lineage-variant>span{color:var(--muted)}.lineage-compound{background:#e5dfd2;padding:1rem}.lineage-compound>span{color:var(--ink)}
.compound-divider{min-height:56vh;padding:clamp(4rem,8vw,8rem) max(5vw,calc((100vw - 1380px)/2));display:grid;grid-template-columns:minmax(10rem,.35fr) minmax(18rem,.75fr) minmax(22rem,.9fr);gap:clamp(2rem,5vw,5rem);align-items:center;background:var(--ink);color:var(--paper-2);border-top:1px solid var(--rule)}.compound-divider p{margin:0;font-size:.68rem;letter-spacing:.16em;font-weight:850}.compound-divider h3{margin:0;font-family:var(--serif);font-size:clamp(2.6rem,5vw,5.4rem);line-height:1}.compound-divider span{max-width:48ch;color:#cbd3d7;font-size:.8rem;line-height:1.65}
@media(max-width:760px){.pattern-lineage,.compound-divider{grid-template-columns:1fr}.compound-divider{min-height:auto}.directory-pattern>a{grid-template-columns:1fr}.directory-role{display:block}}
@media(max-width:560px){.pattern-lineage{gap:.7rem}.lineage-variant{padding-left:.7rem}.lineage-compound{margin-left:-.7rem;margin-right:-.7rem}.compound-divider{padding-left:1.2rem;padding-right:1.2rem}}
@media print{.pattern-lineage{break-inside:avoid}.lineage-compound{background:var(--paper)!important}.compound-divider,.compound-divider[hidden]{display:grid!important;min-height:0;break-before:page;break-after:page;background:var(--paper-2)!important;color:var(--ink)!important}.compound-divider span{color:var(--ink)!important}}
'''

CSS += r'''
.taxonomy-tags{display:flex;flex-wrap:wrap;gap:.45rem;margin:.8rem 0 0}.taxonomy-badge{display:inline-flex;align-items:center;gap:.45rem;width:max-content;max-width:100%;padding:.3rem .55rem;border:1px solid var(--rule);background:var(--paper-2);font-size:.61rem;line-height:1.35;font-weight:750;text-decoration:none}.taxonomy-badge:before{content:"TAXONOMY";font-size:.5rem;letter-spacing:.09em;color:var(--muted)}.taxonomy-badge:hover{border-color:var(--ink)}
.taxonomy-hero{padding:clamp(4rem,8vw,8rem) max(5vw,calc((100vw - 1380px)/2));background:var(--ink);color:var(--paper-2)}.taxonomy-hero-grid{display:grid;grid-template-columns:minmax(22rem,1.25fr) minmax(17rem,.75fr);gap:7vw;align-items:end}.taxonomy-hero h1{max-width:9ch;margin:.4rem 0 1.5rem;font-family:var(--serif);font-size:clamp(3.7rem,7vw,7.5rem);line-height:.96;letter-spacing:-.055em}.taxonomy-hero p{max-width:64ch;color:#d2d9dc}.taxonomy-hero-rule{margin:0;padding:1rem 0 0;border-top:1px solid #ffffff55;font-family:var(--serif);font-size:clamp(1.1rem,2vw,1.7rem);line-height:1.45}
.taxonomy-tools-wrap{position:sticky;top:4rem;z-index:10;padding:1.6rem max(5vw,calc((100vw - 1380px)/2));background:var(--paper-2);border-bottom:1px solid var(--rule)}.taxonomy-tools{display:grid;grid-template-columns:minmax(13rem,1fr) minmax(17rem,.9fr) auto auto;gap:1rem;align-items:end}.taxonomy-control{display:grid;gap:.35rem}.taxonomy-control label{font-size:.65rem;font-weight:850}.taxonomy-control input,.taxonomy-control select{width:100%;min-height:2.8rem;padding:.65rem .8rem;border:1px solid var(--ink);border-radius:0;background:var(--paper);color:var(--ink);font:inherit;font-size:.78rem}.taxonomy-layer-filters{display:flex;gap:.35rem}.taxonomy-layer-filters button{min-height:2.8rem;padding:.55rem .7rem;border:1px solid var(--rule);background:transparent;color:var(--ink);font:inherit;font-size:.68rem;cursor:pointer}.taxonomy-layer-filters button[aria-pressed=true]{border-color:var(--ink);background:var(--ink);color:var(--paper-2)}.taxonomy-filter-status{min-width:10rem;padding-bottom:.55rem;color:var(--muted);font-size:.7rem;text-align:right}
.taxonomy-overview{padding:clamp(3.5rem,7vw,7rem) max(5vw,calc((100vw - 1380px)/2));background:#e9e4da}.taxonomy-overview header{display:grid;grid-template-columns:.55fr 1.45fr;gap:5vw;align-items:end;margin-bottom:2.5rem}.taxonomy-overview h2{margin:0;font-family:var(--serif);font-size:clamp(2.5rem,5vw,5rem);line-height:1}.taxonomy-overview header p{max-width:65ch;margin:0;color:var(--muted)}.taxonomy-overview-grid{display:grid;grid-template-columns:repeat(4,1fr);border-top:2px solid var(--ink);border-bottom:1px solid var(--ink)}.taxonomy-overview-column{padding:1.1rem;border-right:1px solid var(--rule)}.taxonomy-overview-column:last-child{border-right:0}.taxonomy-overview-column h3{margin:0 0 .75rem;font-family:var(--serif);font-size:1.25rem}.taxonomy-overview-column ol{margin:0;padding:0;list-style:none}.taxonomy-overview-column li{border-top:1px solid var(--rule)}.taxonomy-overview-column a{display:flex;justify-content:space-between;gap:.7rem;padding:.55rem 0;text-decoration:none;font-size:.68rem}.taxonomy-overview-column b{font-family:var(--serif);font-size:.85rem}
.taxonomy-results{background:var(--paper)}.taxonomy-group{padding:clamp(4rem,8vw,8rem) max(5vw,calc((100vw - 1380px)/2));border-bottom:1px solid var(--rule);scroll-margin-top:10rem}.taxonomy-group:nth-of-type(even){background:var(--paper-2)}.taxonomy-group-header{display:grid;grid-template-columns:5rem minmax(17rem,.8fr) minmax(20rem,1.2fr) 4rem;gap:clamp(1rem,4vw,4rem);align-items:start;margin-bottom:2.5rem;padding-top:.8rem;border-top:2px solid var(--ink)}.taxonomy-group-layer{font-family:var(--serif);font-size:1.4rem;font-weight:850}.taxonomy-group h2{margin:0;font-family:var(--serif);font-size:clamp(2rem,4vw,4rem);line-height:1}.taxonomy-group h2 small{display:block;margin-top:.5rem;color:var(--muted);font-family:var(--sans);font-size:.23em;line-height:1.4;letter-spacing:.06em;text-transform:uppercase}.taxonomy-group-header p{max-width:65ch;margin:0;color:var(--muted);font-size:.82rem}.taxonomy-group-count{text-align:right;font-family:var(--serif);font-size:1.5rem}.taxonomy-patterns{margin:0;padding:0;list-style:none;border-top:1px solid var(--ink)}.taxonomy-pattern{border-bottom:1px solid var(--rule)}.taxonomy-pattern>a{display:grid;grid-template-columns:3rem minmax(15rem,.7fr) minmax(20rem,1.3fr) 7rem 1.5rem;gap:1rem;align-items:baseline;padding:1rem 0;text-decoration:none}.taxonomy-pattern-index{font-family:var(--serif);font-weight:850}.taxonomy-pattern-name strong{display:block;font-family:var(--serif);font-size:1.08rem}.taxonomy-pattern-name small{display:block;color:var(--muted);font-size:.66rem}.taxonomy-pattern-intent{margin:0;color:var(--muted);font-size:.73rem;line-height:1.55}.taxonomy-role{font-size:.58rem;letter-spacing:.09em;font-weight:850;text-align:right}.taxonomy-role.role-common{color:var(--l3)}.taxonomy-role.role-variant{color:var(--muted)}.taxonomy-role.role-compound{color:var(--enabler)}.taxonomy-pattern-arrow{text-align:right}.taxonomy-page .publication-note{border-top:1px solid var(--rule)}
@media(max-width:1000px){.taxonomy-hero-grid,.taxonomy-overview header{grid-template-columns:1fr}.taxonomy-tools{grid-template-columns:1fr 1fr}.taxonomy-filter-status{text-align:left}.taxonomy-overview-grid{grid-template-columns:repeat(2,1fr)}.taxonomy-overview-column:nth-child(2){border-right:0}.taxonomy-overview-column:nth-child(-n+2){border-bottom:1px solid var(--rule)}.taxonomy-group-header{grid-template-columns:4rem 1fr}.taxonomy-group-header p{grid-column:2}.taxonomy-group-count{grid-column:1;grid-row:2;text-align:left}.taxonomy-pattern>a{grid-template-columns:2.5rem minmax(14rem,.8fr) minmax(16rem,1.2fr) 6rem 1rem}}
@media(max-width:700px){.taxonomy-tools-wrap{position:static}.taxonomy-tools{grid-template-columns:1fr}.taxonomy-layer-filters{flex-wrap:wrap}.taxonomy-overview-grid{grid-template-columns:1fr}.taxonomy-overview-column{border-right:0;border-bottom:1px solid var(--rule)}.taxonomy-overview-column:nth-child(-n+2){border-bottom:1px solid var(--rule)}.taxonomy-overview-column:last-child{border-bottom:0}.taxonomy-group-header{grid-template-columns:1fr;gap:.7rem}.taxonomy-group-header p,.taxonomy-group-count{grid-column:1;grid-row:auto}.taxonomy-pattern>a{grid-template-columns:2.3rem 1fr 5.5rem 1rem}.taxonomy-pattern-intent{grid-column:2 / -1}.taxonomy-role{grid-column:2;text-align:left;white-space:nowrap}.taxonomy-pattern-arrow{grid-column:4;grid-row:3}.taxonomy-pattern-name strong{font-size:1rem}}
@media(max-width:560px){.taxonomy-hero,.taxonomy-tools-wrap,.taxonomy-overview,.taxonomy-group{padding-left:1.2rem;padding-right:1.2rem}.taxonomy-hero h1{font-size:3.5rem}.taxonomy-badge{white-space:normal}}
@media print{.taxonomy-tools-wrap{display:none!important}.taxonomy-overview,.taxonomy-group{break-before:page}.taxonomy-group[hidden],.taxonomy-pattern[hidden]{display:block!important}.taxonomy-pattern>a{grid-template-columns:2rem 1fr 1.2fr 5rem 1rem}.taxonomy-hero{background:var(--paper-2)!important;color:var(--ink)!important}.taxonomy-hero p{color:var(--ink)!important}}
'''

CSS += r'''
.enablers .layer-header{background:#e8dfc8;color:var(--ink);border-top:2px solid var(--enabler);border-bottom:2px solid var(--enabler)}.enablers .layer-number{font-family:var(--sans);font-size:clamp(2.4rem,6vw,6rem);letter-spacing:-.05em;color:var(--enabler)}.enabler-boundary{max-width:62ch!important;color:var(--muted)!important;font-size:.78rem!important;letter-spacing:0!important;text-transform:none!important}.entry-enabler .pattern-kicker{border-top-color:var(--enabler)}.entry-enabler .pattern-kicker>span:first-child{color:var(--enabler);font-weight:900}.directory-enablers{background:#eee7d7}.directory-enablers h2{color:var(--enabler)}.taxonomy-overview-enablers{background:#eee7d7}.taxonomy-role.role-enabler{color:var(--enabler)}.taxonomy-enabler{background:color-mix(in oklab,var(--paper-2) 78%,#e8dfc8)}.taxonomy-group[data-layer="E"] .taxonomy-group-layer{color:var(--enabler)}.taxonomy-group[data-layer="E"] .taxonomy-group-header{border-top-color:var(--enabler)}
@media print{.enablers .layer-header{background:var(--paper-2)!important;color:var(--ink)!important}.taxonomy-enabler{background:var(--paper-2)!important}}
'''

CSS += r'''
/* English is the canonical display name; Chinese remains a quiet translation aid. */
.term-en{font-family:var(--serif);font-weight:750;color:inherit}.term-zh,.localized-name{display:block;margin:.32rem 0 0;color:var(--muted);font-family:var(--sans);font-size:.72em;font-weight:520;line-height:1.35;letter-spacing:.02em}.bilingual-name-inline{display:inline-flex;flex-direction:column;align-items:flex-start;line-height:1.25}.bilingual-name-inline>.term-zh{font-size:.72em}.pattern-heading .localized-name{font-size:clamp(.82rem,1vw,1.05rem)}.anchor-index strong>.term-en{display:block}.anchor-index strong>.term-zh{font-size:.62rem}.pattern-lineage .bilingual-name-inline{font-size:.9rem}.pattern-lineage .term-zh{font-size:.66rem}.directory-column .term-en{font-size:.72rem}.directory-column .term-zh{font-size:.58rem}.taxonomy-badge.bilingual-name-inline{align-items:flex-start;gap:.12rem}.taxonomy-badge .term-zh{font-size:.54rem}.taxonomy-overview-column .term-en{font-size:.7rem}.taxonomy-overview-column .term-zh{font-size:.58rem}.taxonomy-group h2 small{font-size:.25em;text-transform:none}.taxonomy-pattern-name small{font-weight:520;letter-spacing:.02em}
'''


def canonical_url(path):
    base = os.environ.get("ATLAS_PUBLIC_BASE_URL", "").rstrip("/")
    return f"{base}/{path.lstrip('/')}" if base else ""


def render_head(title, description, path, schema_type="TechArticle", script_name=None):
    url = canonical_url(path)
    image_url = canonical_url("assets/social-card.svg")
    schema = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "headline": title,
        "description": description,
        "inLanguage": "zh-Hans",
        "author": {"@type": BLOG["author_type"], "name": BLOG["author"]},
        "datePublished": BLOG["published"],
        "dateModified": BLOG["modified"],
    }
    if url:
        schema["image"] = image_url
        schema["url"] = url
    script = f'<script src="assets/{script_name}" defer></script>' if script_name else ""
    robots = "index,follow,max-image-preview:large" if url else "noindex,follow"
    canonical = f'<link rel="canonical" href="{esc(url)}">' if url else ""
    public_meta = "" if not url else f'''
<meta property="og:url" content="{esc(url)}"><meta property="og:image" content="{esc(image_url)}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(description)}"><meta name="twitter:image" content="{esc(image_url)}">'''
    return f'''<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}"><meta name="author" content="{esc(BLOG['author'])}">
<meta name="robots" content="{robots}"><meta name="theme-color" content="#172331">
{canonical}<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<meta property="og:type" content="{'article' if schema_type == 'TechArticle' else 'website'}"><meta property="og:locale" content="zh_CN">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}">{public_meta}
<meta property="article:published_time" content="{BLOG['published']}"><meta property="article:modified_time" content="{BLOG['modified']}">
<link rel="stylesheet" href="assets/article.css">{script}
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace('</', '<\\/')}</script>
</head>'''


def site_nav(active):
    links = [
        ("article", "index.html", "文章主线"),
        ("atlas", "atlas.html", "完整图鉴"),
        ("taxonomy", "taxonomy.html", "分类浏览"),
        ("sources", "atlas.html#coverage", "覆盖与来源"),
    ]
    rendered = "".join(
        f'<a href="{href}"{(" aria-current=\"page\"" if key == active else "")}>{label}</a>'
        for key, href, label in links
    )
    return f'<nav class="site-nav" aria-label="主要导航"><a class="site-mark" href="index.html" aria-label="Agentic Pattern Atlas 首页">AP / ATLAS</a><div class="site-links">{rendered}</div></nav>'


def diagram_img(name, alt, eager=False):
    loading = ' loading="eager" fetchpriority="high"' if eager else ' loading="eager" fetchpriority="low"'
    return f'<img src="diagrams/{name}.svg" alt="{esc(alt)}" width="1200" height="675" decoding="async"{loading}>'


def render_case_study_svg():
    uid = "enterprise-exception-case"
    rows = [
        ("L1", 130, LAYER_META["L1"]["color"], [(210, "业务处理人员", "human"), (505, "Exception Copilot", "agent"), (835, "处置审批", "human")]),
        ("L2", 250, LAYER_META["L2"]["color"], [(210, "Workflow", "workflow"), (505, "Supervisor", "agent"), (835, "领域 Agents", "agent")]),
        ("L3", 370, LAYER_META["L3"]["color"], [(170, "ReAct", "agent"), (410, "Plan + Execute", "agent"), (650, "RAG", "tool"), (890, "HITL", "policy")]),
        ("ENABLERS", 500, ENABLER_META["color"], [(210, "Context", "memory"), (505, "MCP", "external"), (835, "Trace / Evals", "memory")]),
    ]
    parts = []
    for layer, y, color, items in rows:
        parts.append(f'<rect x="50" y="{y-15}" width="1095" height="92" rx="10" fill="{color}" opacity=".07" stroke="{color}" stroke-width="1"/>')
        parts.append(f'<text x="75" y="{y+38}" font-size="24" font-weight="800" fill="{color}">{layer}</text>')
        for x, label, role in items:
            width = 165
            parts.append(node(x, y, width, 64, label, role))
        for left, right in zip(items, items[1:]):
            lx = left[0] + 165
            parts.append(arrow(lx, y+32, right[0], y+32, style="data" if layer == "ENABLERS" else "control"))
    parts += [arrow(585, 194, 585, 250, "约束"), arrow(585, 314, 585, 370, "调度"), arrow(585, 434, 585, 500, "implemented with", "data")]
    body = "".join(parts).replace('url(#arrow)', f'url(#arrow-{uid})')
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 675" role="img" aria-labelledby="title-{uid} desc-{uid}"><title id="title-{uid}">企业异常事件诊断与处置的三层 Pattern 与实现手段组合</title><desc id="desc-{uid}">L1 业务责任、L2 系统架构和 L3 设计结构构成三个 Pattern 层级；Context、MCP 与 Trace 作为不编号的实现手段支撑这些 Pattern。</desc><defs><marker id="arrow-{uid}" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="context-stroke"/></marker></defs><rect width="1200" height="675" fill="{PALETTE['paper2']}"/><text x="55" y="66" font-family="Iowan Old Style, Songti SC, serif" font-size="34" font-weight="700" fill="{PALETTE['ink']}">三个 Pattern 层级，由实现手段支撑</text><text x="1145" y="64" text-anchor="end" font-size="15" fill="{PALETTE['muted']}">Enterprise exception handling</text><g font-family="Avenir Next, PingFang SC, sans-serif">{body}</g><text x="55" y="640" font-size="14" fill="{PALETTE['muted']}">ENABLERS 不是第四层 Pattern；它们可以被多个层级复用或替换。</text></svg>'''


def render_social_card_svg():
    return f'''<?xml version="1.0" encoding="UTF-8"?><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630"><rect width="1200" height="630" fill="{PALETTE['ink']}"/><circle cx="1085" cy="-40" r="320" fill="none" stroke="#ffffff18" stroke-width="2"/><circle cx="1085" cy="-40" r="245" fill="none" stroke="#ffffff10" stroke-width="55"/><text x="72" y="80" font-family="Avenir Next, PingFang SC, sans-serif" font-size="17" font-weight="750" letter-spacing="3" fill="#c9d1d5">AGENTIC PATTERN ATLAS · 2026</text><text x="72" y="205" font-family="Iowan Old Style, Songti SC, serif" font-size="72" font-weight="700" fill="{PALETTE['paper2']}">先看见结构，再谈论 Pattern</text><text x="72" y="285" font-family="Iowan Old Style, Songti SC, serif" font-size="46" font-weight="700" fill="{PALETTE['paper2']}">Agentic AI 三层 Pattern 视觉图鉴</text><text x="72" y="350" font-family="Avenir Next, PingFang SC, sans-serif" font-size="24" fill="#cad2d6">Application · Architecture · Design，另列实现手段</text><g font-family="Avenir Next, PingFang SC, sans-serif" font-size="18" font-weight="750"><rect x="72" y="480" width="264" height="72" fill="{LAYER_META['L1']['color']}"/><text x="94" y="524" fill="{PALETTE['paper2']}">L1 · Application</text><rect x="336" y="480" width="264" height="72" fill="{LAYER_META['L2']['color']}"/><text x="358" y="524" fill="{PALETTE['paper2']}">L2 · Architecture</text><rect x="600" y="480" width="264" height="72" fill="{LAYER_META['L3']['color']}"/><text x="622" y="524" fill="{PALETTE['paper2']}">L3 · Design</text><rect x="864" y="480" width="264" height="72" fill="#2b3540" stroke="{ENABLER_META['color']}" stroke-width="2"/><text x="886" y="524" fill="#dfc98d">ENABLERS</text></g></svg>'''


def reference_items(source_ids):
    return "".join(
        f'<li><a href="{esc(SOURCES[sid]["url"])}" target="_blank" rel="noopener noreferrer">{esc(SOURCES[sid]["title"])}</a><span>{esc(SOURCES[sid]["author"])} · {esc(source_note(SOURCES[sid]))}</span></li>'
        for sid in source_ids
    )


def render_comparison(comparison):
    head = "".join(f'<th scope="col">{esc(col)}</th>' for col in comparison["columns"])
    rows = "".join("<tr>" + "".join(f'<td>{esc(cell)}</td>' for cell in row) + "</tr>" for row in comparison["rows"])
    return f'''<section class="comparison-block" id="{esc(comparison['id'])}"><header><h3>{esc(comparison['title'])}</h3><p>{esc(comparison['lead'])}</p></header><div class="comparison-wrap" tabindex="0" role="region" aria-label="{esc(comparison['title'])}比较表"><table class="comparison-table"><caption class="visually-hidden">{esc(comparison['title'])}</caption><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div><p class="comparison-summary">{esc(comparison['summary'])}</p></section>'''


def render_blog():
    by_id = {p["id"]: p for p in PATTERNS}
    entry_count = len(PATTERNS)
    pattern_count = sum(p["catalog_type"] == "pattern" for p in PATTERNS)
    enabler_count = entry_count - pattern_count
    anchor_count = len(ANCHOR_IDS)
    comparison_count = len(COMPARISONS)
    paths = "".join(f'<a class="reading-path" href="{href}"><strong>{esc(title)}</strong><span>{esc(detail)}</span></a>' for title, detail, href in READING_PATHS)
    case_rows = "".join(f'<article><b>{esc(step["layer"])}</b><small>{esc(step["question"])}</small><strong>{esc(step["choice"])}</strong><p>{esc(step["reason"])}</p></article>' for step in CASE_STEPS)
    anchors = "".join(f'<li><a href="atlas.html#{p["id"]}"><span class="anchor-layer">{"ENABLER" if p["catalog_type"] == "enabler" else p["layer"]}</span><strong>{bilingual_name(p)}</strong><p>{esc(p["intent"])}</p><em>{esc(p["provenance"])}</em></a></li>' for p in (by_id[i] for i in ANCHOR_IDS))
    decisions = "".join(f'<article><b>{n}</b><h3>{esc(q)}</h3><p>{esc(answer)}</p></article>' for n, q, answer in DECISION_QUESTIONS)
    published = f'<time datetime="{BLOG["published"]}">{BLOG["published"]}</time>'
    return f'''<!doctype html><html lang="zh-Hans">{render_head(BLOG['title'], BLOG['description'], 'index.html')}
<body class="blog-page"><a class="skip-link" href="#main">跳到正文</a>{site_nav('article')}
<header class="hero"><div class="hero-grid"><div class="edition">FIELD GUIDE · {BLOG['version']}</div><div class="hero-copy"><p class="eyebrow">Agentic AI 应用架构模式</p><h1>先看见结构，<br>再谈论 Pattern。<small>Agentic AI 三层 Pattern 视觉图鉴</small></h1><p class="deck">{esc(BLOG['subtitle'])}</p><div class="article-meta"><span>{esc(BLOG['author'])}</span><span>{published}</span><span>{esc(BLOG['reading_time'])}</span><span>{pattern_count} Pattern + {enabler_count} Enablers</span></div><div class="hero-actions"><a href="#problem">开始阅读</a><a href="atlas.html">打开完整图鉴</a></div></div><div class="hero-index"><a href="#map"><b>01</b><span>三层地图</span><em>3L</em></a><a href="#case"><b>02</b><span>组合示例</span><em>1</em></a><a href="#comparisons"><b>03</b><span>关键比较</span><em>{comparison_count}</em></a><a href="atlas.html"><b>04</b><span>完整图鉴</span><em>{entry_count}</em></a></div></div><div class="hero-rule"><span>Application</span><span>Architecture</span><span>Design</span><span>Enablers</span></div></header>
<main id="main">
<section class="reading-paths" aria-labelledby="reading-title"><header><p class="eyebrow">选择阅读深度</p><h2 id="reading-title">从主线进入，按需下钻。</h2></header>{paths}</section>
<section class="content-section problem-section" id="problem"><div class="chapter-mark"><span>01</span><div><h2>这是一个无法正确回答的四选一。</h2><p>为企业异常事件诊断与处置助手选架构时，人们常问：应该用 ReAct、Multi-Agent、RAG，还是 MCP？问题本身混合了 Pattern 层级与实现手段。</p></div></div><div class="problem-grid"><p class="impossible-question">ReAct、Multi-Agent、RAG 和 MCP 可以同时存在于同一个系统，它们不是互斥选项。</p><div class="wrong-choice"><b>四个词分别回答什么</b><p>先辨认问题类型，才可能讨论选择。</p><div class="four-answers"><div><strong>ReAct</strong><span>一个 Agent 怎样决定下一步</span></div><div><strong>Multi-Agent</strong><span>多个自治单元怎样组织</span></div><div><strong>RAG</strong><span>知识检索怎样进入生成结构</span></div><div><strong>MCP</strong><span>Agent Host 怎样连接外部能力</span></div></div></div></div><ol class="thesis-list"><li>Pattern 分类应跟随目标所有权、控制权、自治边界、状态和协作关系，而不是部署单元。</li><li>不同层级的 Pattern 是组合关系，不是竞争关系。</li><li>协议、技术和工程实践可以实现 Pattern，却不能替代结构决策。</li><li>默认选择满足目标的最小自治与最小协调结构。</li></ol></section>
<section class="content-section map-section" id="map"><div class="chapter-mark"><span>02</span><div><h2>先确定 System of Interest。</h2><p>三个 Pattern 层级回答不同尺度的结构问题；实现手段则横向支撑这些结构，不再被包装成第四层。</p></div></div><div class="map-layout"><div><div class="diagnostic-questions"><div><b>L1</b><span>Agent 在业务责任体系中处于什么位置？</span></div><div><b>L2</b><span>一个或多个 Agent 如何组织和分配控制权？</span></div><div><b>L3</b><span>Agent 与局部控制结构如何完成决策和行动？</span></div><div><b>TOOLS</b><span>哪些技术、协议、格式与实践支撑这些 Pattern？</span></div></div><p>判断 Pattern 前，先问：这一刻我们把什么当作完整系统？</p></div><figure class="diagram-viewport" tabindex="0" role="region" aria-label="三层 Pattern 与实现手段地图">{diagram_img('three-level-pattern-map', '三层 Pattern 地图：Application、Architecture、Design，以及独立的实现手段目录', True)}<figcaption>前三项是 Pattern 层级；Enablers 是可跨层复用和替换的实现手段。</figcaption></figure></div></section>
<section class="taxonomy"><p class="section-label">分类边界</p><h2>三层 Pattern，一组独立的实现手段。</h2><div class="taxonomy-grid"><div><b>Application Pattern</b><p>定义 Agent 与人在业务责任体系中的相对位置。</p><small>Copilot · Front Door · Autonomous Worker</small></div><div><b>Architecture Pattern</b><p>改变多个自治单元的责任分配、控制权和系统结构。</p><small>Supervisor · Handoff · Workflow-Centric</small></div><div><b>Design Pattern</b><p>在既定系统边界内组织 Agent 决策、行动和局部控制流。</p><small>ReAct · Prompt Chaining · RAG</small></div><div><b>Techniques / Protocols / Practices</b><p>提供实现方法、连接契约或工程保障，本身不构成第四层 Pattern。</p><small>Context · Memory · MCP · A2A · Evals</small></div></div></section>
<section class="case-section" id="case"><div class="chapter-mark"><span>03</span><div><h2>一个企业异常处置示例，组合三层 Pattern 与实现手段。</h2><p>某笔订单的状态、履约记录与客户反馈互相矛盾。系统需要查询业务记录、相关系统和处置规则，形成原因假设并给出方案；退款、状态变更或外部通知必须由业务人员审批。</p></div></div><p class="case-brief">这里没有“一个最佳 Pattern”：三个 System of Interest 分别做出结构决定，再由实现手段支撑。</p><figure class="case-figure diagram-viewport" tabindex="0" role="region" aria-label="企业异常事件诊断与处置三层 Pattern 组合图">{diagram_img('enterprise-exception-case', '企业异常事件诊断与处置的三层 Pattern 与实现手段组合', True)}<figcaption>从业务责任到系统控制和 Agent 设计，三个层级构成结构；Context、MCP 与评估等手段支撑实现。</figcaption></figure><div class="case-grid">{case_rows}</div><p class="case-conclusion">Copilot 定义人机责任；Workflow 与 Supervisor 定义系统控制权；ReAct、RAG 与 HITL 定义局部设计；Context、MCP 与 Trace / Evals 提供实现支撑。</p><a class="skip-to-conclusion" href="#conclusion">已理解三层组合？跳到结论，完成 5 分钟速读 →</a></section>
<section class="anchor-section" id="anchors"><div class="chapter-mark"><span>04</span><div><h2>先记住这 {anchor_count} 个锚点。</h2><p>它们不是完整清单，而是一组可以支撑主叙事的坐标。点击任一条目进入完整视觉图鉴。</p></div></div><ol class="anchor-index">{anchors}</ol></section>
<section class="comparisons" id="comparisons"><div class="chapter-mark"><span>05</span><div><h2>相似拓扑，可能拥有完全不同的控制语义。</h2><p>以下 {comparison_count} 组比较围绕控制权、Agent 身份、生命周期、通信方式和结果回收展开。</p></div></div>{''.join(render_comparison(c) for c in COMPARISONS)}</section>
<section class="decision-section" id="decision"><div class="chapter-mark"><span>06</span><div><h2>选择 Pattern，从四个问题开始。</h2><p>架构不是按流行度点菜，而是对业务责任、控制权、状态和质量属性做出可解释的取舍。</p></div></div><div class="decision-grid">{decisions}</div><p class="default-rule">默认原则：选择能够满足目标的最小自治、最小协调结构。每增加一层自治，都同步增加停止条件、权限边界、恢复、评估和可观测设计。</p></section>
<section class="tradeoffs" id="tradeoffs"><p class="section-label">选择原则</p><h2>Architecture is about trade-offs.</h2><div class="tradeoff-line"><span>Autonomy</span><span>Safety</span><span>Reliability</span><span>Latency</span><span>Cost</span><span>Observability</span><span>Maintainability</span></div><p>没有抽象意义上的最佳 Pattern。Pattern 选择必须回应业务重要性、技术难度、失败代价和约束条件；高自主性通常同时放大权限、安全、恢复、成本与可观测性要求。</p></section>
<section class="conclusion-section" id="conclusion"><div class="chapter-mark"><span>07</span><div><h2>先问层级，再问 Pattern。</h2></div></div><div class="conclusion-copy"><p>Agentic 架构不应从“要不要 Multi-Agent”开始，而应从“此刻谁是 System of Interest”开始。先在 L1 明确人与 Agent 的业务责任，再在 L2 决定控制权和协作拓扑，在 L3 选择 Agent 的决策、行动与局部控制结构；确定结构后，再配置上下文、记忆、协议、安全和可观测等实现手段。</p><p>ReAct 不能替代 Supervisor，MCP 不能替代 Handoff，RAG 也不能回答谁拥有业务责任。前两者分别属于 Design 与 Architecture Pattern，MCP 则是可被多种结构复用的协议。</p></div><div class="atlas-cta"><div><strong>继续下钻</strong><p>完整图鉴包含 {pattern_count} 个 Pattern 与 {enabler_count} 个 Enabler，共 {entry_count} 个条目；每项均包含拓扑、适用条件、权衡、文字案例和精确出处。</p></div><a href="atlas.html">打开完整图鉴 →</a></div></section>
<section class="method-section" id="method"><div class="chapter-mark"><span>08</span><div><h2>方法、来源与引用边界。</h2><p>本文提供一种分析框架，不宣称是行业唯一分类法。原资料称谓与本文分类判断始终并列保留。</p></div></div><div class="method-grid"><article><b>分类声明</b><p>本文按 System of Interest、目标所有权、自治边界、控制权、状态和协作关系重组来源。</p></article><article><b>来源标记</b><p>“来源原名”保留原称谓；“规范化命名”统一来源中的模式族；“本文归纳”明确表示综合性命名。</p></article><article><b>图形声明</b><p>所有拓扑均为本文依据来源重新绘制的静态解释图，不复制来源插图，也不表示部署边界。</p></article><article><b>版本</b><p>版本 {BLOG['version']}，发布于 {BLOG['published']}。来源可能更新，协议细节以各自正式规范为准。</p></article></div><p>ISO/IEC/IEEE 42010:2022 使用更一般的 Entity of Interest。本文聚焦软件与 Agentic 系统，沿用 System of Interest 作为便于分析和讨论的术语；L1 至 L3 与 Enablers 的划分是本文综合框架，并非该标准规定的层级。</p><p>来源引用主要支持模式名称、参与者和结构描述；各条目的适用信号、优势、代价、易混淆项及跨层影响，除非另有说明，均为本文综合分析。</p><p>《Agentic Design Patterns》统一引用 Springer 2025 年第一版和 DOI 10.1007/978-3-032-01402-3，并以 Chapter、Appendix 或小节名称定位。</p><div class="citation-box"><div><h3>建议引用</h3><p>转载或引用图形时，请保留文章标题、版本和原始来源索引；对外转载与二次分发需取得版权主体授权。</p></div><code>{esc(BLOG['author'])}. 《{esc(BLOG['title'])}》, version {BLOG['version']}, {BLOG['published']}.</code></div><div class="compact-references"><h3>主文来源</h3><ol>{reference_items(SELECTED_SOURCE_IDS)}</ol></div></section>
</main><div class="publication-note">本文与 Springer、Anthropic、Microsoft、LangChain、MCP、A2A、Agent Skills 等项目不存在隶属或官方背书关系。正文与原创拓扑 © 2026 {esc(BLOG['author'])}，保留所有权利；引用资料与商标权利归各自权利人。</div><footer class="page-footer"><p>{esc(BLOG['short_title'])} · v{BLOG['version']} · {BLOG['published']}</p><a href="#main">回到正文 ↑</a></footer></body></html>'''


def public_pattern_html(pattern, index):
    by_id = {item["id"]: item for item in PATTERNS}
    is_enabler = pattern["catalog_type"] == "enabler"
    section_label = ENABLER_META["label"] if is_enabler else pattern["layer"]
    case_usage_label = "如何使用" if is_enabler else "Pattern 如何出现"
    source_label = "条目出处" if is_enabler else "Pattern 出处"
    aliases = " · ".join(pattern["aliases"]) if pattern["aliases"] else "无"
    technique = ""
    if pattern["techniques"]:
        technique = '<div class="technique-strip" aria-label="包含技术">' + "".join(f'<span>{esc(t)}</span>' for t in pattern["techniques"]) + "</div>"
    source_terms = " ".join(
        f'{sid} {SOURCES[sid]["title"]} {SOURCES[sid]["author"]}'
        for sid in pattern["sources"]
    )
    case_terms = " ".join([
        pattern["case_study"]["kind"], pattern["case_study"]["project"],
        pattern["case_study"]["title"],
    ])
    organization_terms = [pattern["organization_role"]]
    organization_terms.extend(
        f'{by_id[item_id]["name_zh"]} {by_id[item_id]["name_en"]}'
        for item_id in [*pattern["variants"], *pattern["composed_of"]]
    )
    if pattern["variant_of"]:
        parent = by_id[pattern["variant_of"]]
        organization_terms.append(f'{parent["name_zh"]} {parent["name_en"]}')
    taxonomy = TAXONOMY_GROUPS[pattern["taxonomy_group"]]
    search = " ".join([
        pattern["name_zh"], pattern["name_en"], *pattern["aliases"],
        pattern["kind"], pattern["abstraction_type"], pattern["pattern_family"],
        pattern["provenance"], pattern["intent"], source_terms, case_terms,
        taxonomy["name_zh"], taxonomy["name_en"], taxonomy["description"],
        *organization_terms,
    ])
    role = pattern["organization_role"]
    if role == "common":
        variant_links = "".join(
            f'<a class="bilingual-name-inline" href="#{variant_id}">{bilingual_name(by_id[variant_id])}</a>'
            for variant_id in pattern["variants"]
        )
        organization_html = f'<aside class="pattern-lineage lineage-common" aria-label="Common Pattern 与 Variants"><span>COMMON PATTERN</span><div><b>直接 Variants</b>{variant_links}</div></aside>'
    elif role == "variant":
        parent = by_id[pattern["variant_of"]]
        organization_html = f'<aside class="pattern-lineage lineage-variant" aria-label="Variant 的 Common Pattern"><span>VARIANT</span><div><b>Common Pattern</b><a class="bilingual-name-inline" href="#{parent["id"]}">{bilingual_name(parent)}</a></div></aside>'
    elif role == "compound":
        component_links = "".join(
            f'<a class="bilingual-name-inline" href="#{component_id}">{bilingual_name(by_id[component_id])}</a>'
            for component_id in pattern["composed_of"]
        )
        organization_html = f'<aside class="pattern-lineage lineage-compound" aria-label="Compound Pattern 组成参考"><span>COMPOUND PATTERN</span><div><b>COMPOSED OF</b>{component_links}<p>{esc(pattern["composition_note"])}</p></div></aside>'
    else:
        organization_html = ""
    taxonomy_html = f'<div class="taxonomy-tags"><a class="taxonomy-badge bilingual-name-inline" href="taxonomy.html?group={pattern["taxonomy_group"]}" aria-label="在分类浏览中查看 {esc(taxonomy["name_en"])}（{esc(taxonomy["name_zh"])}）">{bilingual_taxonomy_name(taxonomy)}</a></div>'
    case_study = pattern["case_study"]
    case_references = "".join(
        f'<a href="{esc(reference["url"])}" target="_blank" rel="noopener noreferrer">{esc(reference["label"])} ↗</a>'
        for reference in case_study["references"]
    )
    case_html = f'''<section class="case-study" aria-labelledby="case-{pattern['id']}"><header class="case-study-header"><div><p class="case-kind">CASE · {esc(case_study['kind'])}</p><h4 id="case-{pattern['id']}">{esc(case_study['title'])}</h4></div><p class="case-project">{esc(case_study['project'])}</p></header><div class="case-study-body"><section><h5>项目场景</h5><p>{esc(case_study['scenario'])}</p></section><section><h5>{case_usage_label}</h5><p>{esc(case_study['application'])}</p></section><section><h5>为什么适合</h5><p>{esc(case_study['fit'])}</p></section></div><footer class="case-references"><span>案例依据</span>{case_references}</footer></section>'''
    return f'''<article class="pattern-entry layer-{pattern['layer'].lower()} role-{role}{' entry-enabler' if is_enabler else ''}" id="{pattern['id']}" data-layer="{pattern['layer']}" data-catalog-type="{pattern['catalog_type']}" data-organization="{role}" data-taxonomy="{pattern['taxonomy_group']}" data-search="{esc(search)}" aria-labelledby="heading-{pattern['id']}"><div class="pattern-kicker"><span>{section_label}</span><span>{esc(pattern['kind'])}</span><span class="provenance">{esc(pattern['provenance'])}</span><span>{index:02d}</span></div>{taxonomy_html}{organization_html}<header class="pattern-heading"><div><h3 id="heading-{pattern['id']}" lang="en">{esc(pattern['name_en'])}</h3><p class="localized-name" lang="zh-Hans">{esc(pattern['name_zh'])}</p></div><p class="intent">{esc(pattern['intent'])}</p></header><figure class="topology"><a href="diagrams/{pattern['id']}.svg" aria-label="打开 {esc(pattern['name_en'])}（{esc(pattern['name_zh'])}）独立 SVG">{diagram_img(pattern['id'], pattern['alt_text'])}</a><figcaption>{esc(pattern['diagram_caption'])}</figcaption></figure><div class="pattern-notes"><section><h4>适用信号</h4><p>{esc(pattern['when'])}</p></section><section><h4>带来的能力</h4><p>{esc(pattern['strength'])}</p></section><section><h4>主要代价</h4><p>{esc(pattern['cost'])}</p></section></div><div class="structure-notes"><section><h4>参与者与责任</h4><p>{esc(pattern['participants'])}</p></section><section><h4>关系语义</h4><p>{esc(pattern['relationships'])}</p></section><section><h4>跨层影响</h4><p>{esc(pattern['cross_layer'])}</p></section><section><h4>配套机制</h4><p>{esc(pattern['companions'])}</p></section></div><div class="boundary-note"><div><span>{esc(pattern['alias_status'])}</span><p>{esc(aliases)}</p></div><div><span>不要混淆</span><p>{esc(pattern['confusion'])}</p></div><div><span>本文归类</span><p>{esc(pattern['classification'])} {esc(pattern['provenance_note'])}</p></div></div>{technique}{case_html}<footer class="pattern-sources"><span>{source_label}</span>{cite_html(pattern)}</footer></article>'''


def directory_column_html(layer, meta, layer_patterns):
    by_id = {pattern["id"]: pattern for pattern in PATTERNS}
    compounds = [pattern for pattern in layer_patterns if pattern["organization_role"] == "compound"]
    roots = [pattern for pattern in layer_patterns if pattern["organization_role"] not in {"variant", "compound"}]
    items = []
    for pattern in roots:
        relation = '<span class="directory-role">COMMON</span>' if pattern["organization_role"] == "common" else ""
        variants = ""
        if pattern["variants"]:
            variants = '<ol class="directory-variants" aria-label="Variants">' + "".join(
                f'<li><a href="#{variant_id}"><span>VARIANT</span><span class="bilingual-name-inline">{bilingual_name(by_id[variant_id])}</span></a></li>'
                for variant_id in pattern["variants"]
            ) + "</ol>"
        items.append(f'<li class="directory-pattern"><a href="#{pattern["id"]}"><span class="bilingual-name-inline">{bilingual_name(pattern)}</span>{relation}</a>{variants}</li>')
    compounds_html = ""
    if compounds:
        compounds_html = '<div class="directory-compounds"><h3>COMPOUND PATTERNS</h3><ol>' + "".join(
            f'<li><a class="bilingual-name-inline" href="#{pattern["id"]}">{bilingual_name(pattern)}</a></li>'
            for pattern in compounds
        ) + "</ol></div>"
    label = "ENABLERS" if layer == "E" else layer
    return f'<section class="directory-column directory-{layer.lower()}{" directory-enablers" if layer == "E" else ""}"><h2>{label} · {esc(meta["title"])}</h2><ol>{"".join(items)}</ol>{compounds_html}</section>'


def public_coverage_table_html():
    chapter_to_pattern = {}
    for pattern in PATTERNS:
        if pattern["book_chapter"]:
            chapter_to_pattern.setdefault(pattern["book_chapter"], []).append(pattern)
    fallback = {5:"tool-use",7:"supervisor-specialist",8:"memory-management",9:"learning-adaptation",10:"mcp",12:"exception-recovery",13:"human-in-loop",14:"rag",15:"a2a",16:"resource-aware",18:"guardrails",19:"evaluation-monitoring"}
    by_id = {p["id"]: p for p in PATTERNS}
    rows = []
    for n, title, start, end in CHAPTERS:
        pats = chapter_to_pattern.get(n, []) or ([by_id[fallback[n]]] if n in fallback else [])
        links = ", ".join(f'<a class="bilingual-name-inline" href="#{p["id"]}">{bilingual_name(p)}</a>' for p in pats)
        layer = " / ".join(sorted({"ENABLER" if p["layer"] == "E" else p["layer"] for p in pats}))
        kind = "；".join(sorted({p["kind"] for p in pats}))
        source = SOURCES["adp-official"]
        rows.append(f'<tr><td>{n:02d}</td><td><a href="{esc(source["url"])}" target="_blank" rel="noopener noreferrer">{esc(title.replace("_", "/"))}</a></td><td><span class="layer-token {layer.lower().replace(" / ", " ")}">{layer}</span></td><td>{links}</td><td>{esc(kind)}</td><td>Springer 2025 · Chapter {n}</td></tr>')
    return "".join(rows)


def taxonomy_pattern_html(pattern, index):
    role = pattern["organization_role"]
    is_enabler = pattern["catalog_type"] == "enabler"
    role_label = "ENABLER" if is_enabler else {
        "common": "COMMON",
        "variant": "VARIANT",
        "compound": "COMPOUND",
        "standalone": "PATTERN",
    }[role]
    role_class = "enabler" if is_enabler else role
    group = TAXONOMY_GROUPS[pattern["taxonomy_group"]]
    search = " ".join([
        pattern["id"], pattern["name_zh"], pattern["name_en"], *pattern["aliases"],
        pattern["intent"], pattern["kind"],
        pattern["organization_role"], group["name_zh"], group["name_en"],
    ])
    return f'''<li class="taxonomy-pattern{' taxonomy-enabler' if is_enabler else ''}" data-layer="{pattern['layer']}" data-taxonomy="{pattern['taxonomy_group']}" data-search="{esc(search)}"><a href="atlas.html#{pattern['id']}"><span class="taxonomy-pattern-index">{index:02d}</span><span class="taxonomy-pattern-name"><strong lang="en">{esc(pattern['name_en'])}</strong><small lang="zh-Hans">{esc(pattern['name_zh'])}</small></span><p class="taxonomy-pattern-intent">{esc(pattern['intent'])}</p><span class="taxonomy-role role-{role_class}">{role_label}</span><span class="taxonomy-pattern-arrow" aria-hidden="true">↗</span></a></li>'''


def render_taxonomy_page():
    by_id = {pattern["id"]: pattern for pattern in PATTERNS}
    group_sections = []
    group_options = ['<option value="ALL">全部分类</option>']
    overview_columns = []
    index = 0
    catalog_sections = [*LAYER_META.items(), ("E", ENABLER_META)]
    for layer, meta in catalog_sections:
        layer_groups = [
            (group_id, group) for group_id, group in TAXONOMY_GROUPS.items()
            if group["layer"] == layer
        ]
        overview_items = []
        for group_id, group in layer_groups:
            group_options.append(
                f'<option value="{group_id}">{"ENABLERS" if layer == "E" else layer} · {esc(group["name_en"])} · {esc(group["name_zh"])}</option>'
            )
            overview_items.append(
                f'<li><a href="#taxonomy-{group_id}"><span class="bilingual-name-inline">{bilingual_taxonomy_name(group)}</span><b>{len(group["patterns"])}</b></a></li>'
            )
            items = []
            for pattern_id in group["patterns"]:
                index += 1
                items.append(taxonomy_pattern_html(by_id[pattern_id], index))
            group_sections.append(
                f'''<section class="taxonomy-group" id="taxonomy-{group_id}" data-layer="{layer}" data-taxonomy="{group_id}" aria-labelledby="taxonomy-heading-{group_id}"><header class="taxonomy-group-header"><span class="taxonomy-group-layer">{layer}</span><h2 id="taxonomy-heading-{group_id}" lang="en">{esc(group['name_en'])}<small lang="zh-Hans">{esc(group['name_zh'])}</small></h2><p>{esc(group['description'])}</p><span class="taxonomy-group-count">{len(group['patterns'])}</span></header><ol class="taxonomy-patterns">{"".join(items)}</ol></section>'''
            )
        overview_columns.append(
            f'<section class="taxonomy-overview-column{" taxonomy-overview-enablers" if layer == "E" else ""}"><h3>{"ENABLERS" if layer == "E" else layer} · {esc(meta["title"])}</h3><ol>{"".join(overview_items)}</ol></section>'
        )
    pattern_count = sum(pattern["catalog_type"] == "pattern" for pattern in PATTERNS)
    enabler_count = len(PATTERNS) - pattern_count
    description = "按主要架构关注点浏览三层 Agentic Pattern 与独立实现手段；分类不改变 Common、Variant 与 Compound 组织。"
    return f'''<!doctype html><html lang="zh-Hans">{render_head('Agentic Pattern 分类浏览', description, 'taxonomy.html', 'CollectionPage', 'taxonomy.js')}<body class="taxonomy-page"><a class="skip-link" href="#taxonomy-main">跳到分类结果</a>{site_nav('taxonomy')}<header class="taxonomy-hero"><div class="taxonomy-hero-grid"><div><p class="eyebrow">TAXONOMY VIEW · v{BLOG['version']}</p><h1>换一个问题，重新看 {len(PATTERNS)} 个条目。</h1><p>其中 {pattern_count} 个 Pattern 分布在 L1 至 L3；{enabler_count} 个 Techniques、Protocols 与 Practices 单独列出，不构成第四层 Pattern。</p></div><p class="taxonomy-hero-rule">{len(TAXONOMY_GROUPS)} 个互斥的主要关注点组。每个条目只出现一次，Common 与直属 Variant 保持在同一组。</p></div></header><main id="taxonomy-main"><section class="taxonomy-tools-wrap" data-taxonomy-browser><div class="taxonomy-tools"><div class="taxonomy-control"><label for="taxonomy-search">查找条目</label><input id="taxonomy-search" data-taxonomy-search type="search" placeholder="输入名称、意图、类型或角色" autocomplete="off"></div><div class="taxonomy-control"><label for="taxonomy-select">按主要关注点筛选</label><select id="taxonomy-select" data-taxonomy-select>{"".join(group_options)}</select></div><div class="taxonomy-layer-filters" aria-label="按 Pattern 层级或实现手段筛选"><button type="button" data-taxonomy-layer="ALL" aria-pressed="true">全部</button>{''.join(f'<button type="button" data-taxonomy-layer="{layer}" aria-pressed="false">{layer}</button>' for layer in LAYER_META)}<button type="button" data-taxonomy-layer="E" aria-pressed="false">ENABLERS</button></div><div class="taxonomy-filter-status" data-taxonomy-status aria-live="polite">显示 {len(PATTERNS)} / {len(PATTERNS)} 个条目</div></div></section><section class="taxonomy-overview" aria-labelledby="taxonomy-overview-title"><header><h2 id="taxonomy-overview-title">分类是一张索引，不是第二棵树。</h2><p>Pattern 的关注点分类与 Level、Common / Variant、Compound 正交；Enabler 只按工程用途分类，不参与 Pattern 父子关系。</p></header><div class="taxonomy-overview-grid">{"".join(overview_columns)}</div></section><div class="taxonomy-results">{"".join(group_sections)}</div></main><div class="publication-note">Taxonomy Group 是本文用于导航的综合分类；ENABLERS 不构成第四层 Pattern，也不改变 Pattern 之间的组织或组合关系。</div><footer class="page-footer"><p>Agentic Pattern 分类浏览 · v{BLOG['version']} · {BLOG['modified']}</p><a href="#taxonomy-main">回到筛选 ↑</a></footer></body></html>'''


def render_atlas_page():
    entry_count = len(PATTERNS)
    pattern_count = sum(pattern["catalog_type"] == "pattern" for pattern in PATTERNS)
    enabler_count = entry_count - pattern_count
    diagram_count = entry_count + 4
    evidenced_case_count = sum(p["case_study"]["kind"] != "说明性案例" for p in PATTERNS)
    illustrative_case_count = pattern_count - evidenced_case_count
    common_count = sum(pattern["organization_role"] == "common" for pattern in PATTERNS)
    variant_count = sum(pattern["organization_role"] == "variant" for pattern in PATTERNS)
    compound_count = sum(pattern["organization_role"] == "compound" for pattern in PATTERNS)
    nav = []
    sections = []
    directory = []
    count = 0
    for layer, meta in LAYER_META.items():
        layer_patterns = organized_layer_patterns(PATTERNS, layer)
        nav.append(f'<a href="#{layer.lower()}"><b>{layer}</b><span>{esc(meta["title"])}</span><em>{len(layer_patterns)}</em></a>')
        directory.append(directory_column_html(layer, meta, layer_patterns))
        entries = []
        compound_section_started = False
        for pattern in layer_patterns:
            if pattern["organization_role"] == "compound" and not compound_section_started:
                compound_section_started = True
                entries.append(f'<header class="compound-divider" data-layer="{layer}"><p>COMPOUND PATTERNS</p><h3>复合模式单列。</h3><span>它们组合、重复或递归使用多个基础结构，因此不挂在任何单一 Common Pattern 之下。</span></header>')
            count += 1
            entries.append(public_pattern_html(pattern, count))
        if layer == "L1":
            entries.append(f'''<section class="l1-relative-map" id="l1-relative-map" aria-labelledby="l1-relative-title"><div class="l1-relative-copy"><p class="section-label">L1 SYNTHESIS · QUALITATIVE MAP</p><h3 id="l1-relative-title">工作中的人有多近，Agent 又能走多远？</h3><p>这不是四种固定类型的格子，而是四个 Pattern 在两种性质上的相对位置。具体实现可以移动，点与点之间也不存在精确数值。</p><ul class="l1-relative-axes"><li><b>横轴</b>人与执行过程的耦合程度：人无需持续在场 → 人持续参与</li><li><b>纵轴</b>Agent 的任务推进自主度：人或流程主导 → Agent 自主推进</li></ul></div><figure class="l1-relative-figure"><a href="diagrams/l1-human-agent-relative-map.svg" aria-label="打开 L1 人机协作 Pattern 相对性质定位独立 SVG">{diagram_img("l1-human-agent-relative-map", "L1 人机协作 Pattern 相对性质定位：横轴为人与执行过程的耦合程度，纵轴为 Agent 的任务推进自主度")}</a><figcaption>位置只表达相对高低与邻近关系。Continuous Sense–Decide–Act Controller 因持续处理环境反馈闭环，不纳入这张以请求和有界工作项为范围的二维图。</figcaption></figure></section>''')
        sections.append(f'<section class="layer-section {layer.lower()}" id="{layer.lower()}"><header class="layer-header"><span class="layer-number">{layer}</span><div><p>System of Interest</p><h2>{esc(meta["title"])}</h2><blockquote>{esc(meta["question"])}</blockquote></div><span class="layer-count">{len(layer_patterns)}<small>entries</small></span></header>{"".join(entries)}</section>')
    enablers = organized_layer_patterns(PATTERNS, "E")
    directory.append(directory_column_html("E", ENABLER_META, enablers))
    enabler_entries = []
    for entry in enablers:
        count += 1
        enabler_entries.append(public_pattern_html(entry, count))
    sections.append(
        f'<section class="layer-section enablers" id="enablers"><header class="layer-header enabler-header"><span class="layer-number">TOOLS</span><div><p>Implementation repertoire</p><h2>{esc(ENABLER_META["title"])}</h2><blockquote>{esc(ENABLER_META["question"])}</blockquote><p class="enabler-boundary">它们可被多个 Pattern 复用或替换，因此单独编目，不构成 L4。</p></div><span class="layer-count">{enabler_count}<small>entries</small></span></header>{"".join(enabler_entries)}</section>'
    )
    public_reference_sources = {
        sid: src for sid, src in SOURCES.items()
        if sid == "adp-official" or not sid.startswith("adp-")
    }
    source_list = "".join(f'<li id="source-{esc(sid)}"><span>{esc(src["type"])}</span><a href="{esc(src["url"])}" target="_blank" rel="noopener noreferrer">{esc(src["title"])}</a><p>{esc(src["author"])} · {esc(source_note(src))}</p></li>' for sid, src in public_reference_sources.items())
    legend = f'<section class="legend-section" id="legend"><div><p class="section-label">VISUAL LANGUAGE</p><h2>形状表示角色，线条表示关系。</h2><p>颜色不是唯一编码；控制、数据、异步与反馈同时使用不同线型和标签。</p></div><figure class="diagram-viewport" tabindex="0" role="region" aria-label="视觉语法图例">{diagram_img("visual-legend", "Agent、Human、Workflow、Model、Tool、Memory、Policy 与关系线型图例", True)}<figcaption>全文统一使用的实体形状与控制、数据、异步、反馈关系线型。</figcaption></figure></section>'
    return f'''<!doctype html><html lang="zh-Hans">{render_head('Agentic Pattern 完整视觉图鉴', BLOG['description'], 'atlas.html', 'CollectionPage', 'atlas.js')}<body class="atlas-page"><a class="skip-link" href="#atlas-main">跳到图鉴正文</a>{site_nav('atlas')}<header class="atlas-hero"><div class="atlas-hero-grid"><div><p class="eyebrow">REFERENCE ATLAS · v{BLOG['version']}</p><h1>{pattern_count} 个 Pattern，<br>放回三个层级。</h1><p>另有 {enabler_count} 个 Techniques、Protocols 与 Practices 单独编目；它们用于实现 Pattern，但不构成第四层。</p></div><div class="atlas-hero-meta"><span>Pattern <b>{pattern_count}</b></span><span>Implementation Enablers <b>{enabler_count}</b></span><span>Common Groups <b>{common_count}</b></span><span>Direct Variants <b>{variant_count}</b></span><span>Compound Patterns <b>{compound_count}</b></span><span>全部条目 / SVG <b>{entry_count} / {diagram_count}</b></span></div></div></header><main id="atlas-main"><section class="atlas-tools-wrap" data-atlas-browser><div class="atlas-tools"><label for="pattern-search">查找条目</label><input id="pattern-search" data-pattern-search type="search" placeholder="输入名称、Common、Variant、Technique、Protocol、项目或来源" autocomplete="off"><div class="layer-filters" aria-label="按 Pattern 层级或实现手段筛选"><button type="button" data-layer-filter="ALL" aria-pressed="true">全部</button>{''.join(f'<button type="button" data-layer-filter="{layer}" aria-pressed="false">{layer}</button>' for layer in LAYER_META)}<button type="button" data-layer-filter="E" aria-pressed="false">ENABLERS</button></div><div class="filter-status" data-filter-status aria-live="polite">显示 {entry_count} / {entry_count} 个条目</div></div></section><section class="atlas-directory"><div class="chapter-mark"><span>00</span><div><h2>三层 Pattern，一组实现手段。</h2><p>Common + Variant 和 Compound 只组织 L1 至 L3 的 Pattern。Enablers 作为独立目录出现，不参与 Pattern 父子关系。</p></div></div><div class="directory-grid">{"".join(directory)}</div></section>{legend}{''.join(sections)}<section class="tradeoffs" id="tradeoffs"><p class="section-label">选择原则</p><h2>Architecture is about trade-offs.</h2><div class="tradeoff-line"><span>Autonomy</span><span>Safety</span><span>Reliability</span><span>Latency</span><span>Cost</span><span>Observability</span><span>Maintainability</span></div><p>没有抽象意义上的最佳 Pattern。Pattern 选择必须回应业务重要性、技术难度、失败代价和约束条件；实现手段则应服从所选结构。</p></section><section class="coverage" id="coverage"><div class="coverage-title"><p class="section-label">SOURCE → CLASSIFICATION</p><h2>21 个原书章节，逐项落位。</h2><p>原资料使用 Pattern 一词，不代表本文也将其归入 Pattern 层级；Protocol、Technique 与 Practice 会明确标出。</p></div><div class="table-wrap" tabindex="0" role="region" aria-label="原书章节覆盖矩阵"><table><caption class="visually-hidden">Agentic Design Patterns 二十一章覆盖矩阵</caption><thead><tr><th scope="col">Ch.</th><th scope="col">原书主题</th><th scope="col">层级 / 目录</th><th scope="col">图鉴条目</th><th scope="col">本文类型</th><th scope="col">正式定位</th></tr></thead><tbody>{public_coverage_table_html()}</tbody></table></div></section><section class="method-section" id="method"><div class="chapter-mark"><span>∞</span><div><h2>组织、案例与来源声明。</h2><p>只有能够表达稳定参与者、关系、控制流与后果的条目才进入 Pattern 层级。</p></div></div><div class="method-grid"><article><b>三层 Pattern</b><p>L1 描述应用责任，L2 描述系统架构，L3 描述 Agent 与局部控制结构。</p></article><article><b>实现手段</b><p>Technique、Protocol、Practice 与 Capability Format 可被多个 Pattern 复用或替换，因此不编号为 L4。</p></article><article><b>组织关系</b><p>Common + Variant 只用于原子继承；Compound 只单列和交叉链接，不维护单一父节点。</p></article><article><b>版本</b><p>v{BLOG['version']} · {BLOG['modified']}。项目与协议可能更新，以正式资料为准。</p></article></div><p>ISO/IEC/IEEE 42010:2022 使用更一般的 Entity of Interest。本文沿用 System of Interest 作为讨论术语；L1 至 L3 与 Enablers 的划分是本文综合框架，不是该标准规定。</p><p>来源引用主要支持名称、参与者和结构描述；适用信号、权衡、分类及组织关系，除非另有说明，均为本文综合分析。</p></section><section class="references" id="references"><p class="section-label">REFERENCES</p><h2>完整来源索引</h2><ol>{source_list}</ol></section></main><div class="publication-note">本文与列举的产品、开源项目、标准组织及资料发布者不存在隶属或官方背书关系。案例与组织关系用于解释结构映射，不构成对项目实现质量或生产适用性的保证。正文与原创拓扑 © 2026 {esc(BLOG['author'])}，保留所有权利。</div><footer class="page-footer"><p>Agentic Pattern 完整视觉图鉴 · v{BLOG['version']} · {BLOG['modified']}</p><a href="#atlas-main">回到图鉴 ↑</a></footer></body></html>'''


def inline_document(document, script_name=None, atlas_standalone=False, taxonomy_standalone=False):
    standalone = document.replace('<link rel="stylesheet" href="assets/article.css">', f'<style>{CSS}</style>')
    standalone = re.sub(r'<meta name="robots" content="[^"]*">', '<meta name="robots" content="noindex,follow">', standalone)
    standalone = re.sub(r'<link rel="canonical"[^>]*>', '', standalone)
    standalone = re.sub(r'<link rel="icon"[^>]*>', '', standalone)
    standalone = re.sub(r'<meta property="og:[^"]+"[^>]*>', '', standalone)
    standalone = re.sub(r'<meta name="twitter:[^"]+"[^>]*>', '', standalone)
    standalone = re.sub(r'<script type="application/ld\+json">.*?</script>', '', standalone, flags=re.S)
    if script_name:
        script_content = ATLAS_JS if script_name == "atlas.js" else TAXONOMY_JS
        standalone = standalone.replace(f'<script src="assets/{script_name}" defer></script>', f'<script>{script_content}</script>')
    if atlas_standalone:
        def unlink_diagram(match):
            label = match.group(2).replace("打开", "查看").replace("独立 SVG", "拓扑图")
            return f'<div class="diagram-viewport" tabindex="0" role="region" aria-label="{label}">{match.group(3)}</div>'
        standalone = re.sub(r'<a href="diagrams/([^\"]+)\.svg" aria-label="([^\"]+)">(<img\b[^>]*>)</a>', unlink_diagram, standalone)
    for svg_file in sorted(DIAGRAMS.glob("*.svg")):
        svg = svg_file.read_text(encoding="utf-8").split("?>", 1)[-1].strip()
        standalone = standalone.replace(f'href="diagrams/{svg_file.name}"', f'href="#{svg_file.stem}"')
        standalone = re.sub(rf'<img\b[^>]*\bsrc="diagrams/{re.escape(svg_file.name)}"[^>]*>', f'<span class="inline-svg" data-diagram="{svg_file.stem}">{svg}</span>', standalone)
    standalone = standalone.replace('</style>', '.inline-svg{display:block}.inline-svg>svg{display:block;width:100%;height:auto}</style>', 1)
    if atlas_standalone:
        standalone = standalone.replace('href="atlas.html#coverage"', 'href="#coverage"')
        standalone = standalone.replace('href="index.html"', 'href="#atlas-main"').replace('href="atlas.html"', 'href="#atlas-main"')
        standalone = standalone.replace('>文章主线</a>', '>图鉴开头</a>')
    elif taxonomy_standalone:
        standalone = standalone.replace('href="taxonomy.html"', 'href="#taxonomy-main"')
    else:
        standalone = standalone.replace('href="atlas.html#coverage"', 'href="#method"')
        standalone = re.sub(r'href="atlas\.html#[^"]+"', 'href="#anchors"', standalone)
        standalone = standalone.replace('href="atlas.html"', 'href="#anchors"').replace('href="index.html"', 'href="#main"')
        standalone = standalone.replace('打开完整图鉴', '查看锚点索引').replace(
            f'完整查询 {len(PATTERNS)} 个条目',
            f'浏览 {len(ANCHOR_IDS)} 个关键锚点',
        )
        standalone = standalone.replace('按层级、名称和来源检索完整图鉴', '从主文定位最常用的 Pattern')
        standalone = standalone.replace('>完整图鉴</a>', '>锚点索引</a>').replace('>覆盖与来源</a>', '>方法与来源</a>')
    return standalone


def build_intermediates():
    (WORK/"research").mkdir(parents=True,exist_ok=True);(WORK/"design").mkdir(parents=True,exist_ok=True);(WORK/"qa"/"render-review").mkdir(parents=True,exist_ok=True)
    source_lines=["# Source Inventory","",f"- Reference source: {PDF_PATH}","- Historical PDF page locators are research references; a local PDF is not required to build this site.","", "## Registered sources",""]
    for sid,src in SOURCES.items():source_lines.append(f'- **{sid}** — [{src["title"]}]({src["url"]}) — {src["author"]}; {src["locator"]}')
    (WORK/"research"/"source-inventory.md").write_text("\n".join(source_lines)+"\n",encoding="utf-8")
    extract=["# Pattern Extraction","","## Book coverage","", "The book's 21 chapter-level entries are treated as source claims, then reclassified by System of Interest.",""]
    for n,title,start,end in CHAPTERS:
        mapped=[p for p in PATTERNS if p.get("book_chapter")==n or f"adp-{n}" in p["sources"]]
        extract.append(f'### Chapter {n}: {title.replace("_","/")} (PDF {start}-{end})')
        extract.append("- Atlas mapping: "+", ".join(f'{p["name_en"]} → {p["layer"]} ({p["kind"]})' for p in mapped))
    extract += ["","## Appendix A technique families","","Zero/one/few-shot; system and role prompts; delimiters; context engineering; structured output; CoT; self-consistency; step-back; ToT; tool calling; ReAct; APE; iterative prompting; negative examples; analogies; decomposition; RAG; user persona; code and multimodal prompting.","","Classification: implementation enabler, not a numbered Pattern level unless a technique establishes a repeatable participant and control structure."]
    (WORK/"research"/"pattern-extraction.md").write_text("\n".join(extract)+"\n",encoding="utf-8")
    buf=io.StringIO();w=csv.writer(buf);w.writerow(["id","name_zh","name_en","layer","kind","abstraction_type","pattern_family","taxonomy_group","taxonomy_name_zh","taxonomy_name_en","organization_role","variant_of","variants","composed_of","composition_note","provenance","alias_status","aliases","classification","cross_layer","case_kind","case_project","case_title","case_reference_urls","source_ids"])
    for ptn in PATTERNS:w.writerow([ptn["id"],ptn["name_zh"],ptn["name_en"],ptn["layer"],ptn["kind"],ptn["abstraction_type"],ptn["pattern_family"],ptn["taxonomy_group"],ptn["taxonomy_name_zh"],ptn["taxonomy_name_en"],ptn["organization_role"],ptn["variant_of"] or ""," | ".join(ptn["variants"])," | ".join(ptn["composed_of"]),ptn["composition_note"] or "",ptn["provenance"],ptn["alias_status"]," | ".join(ptn["aliases"]),ptn["classification"],ptn["cross_layer"],ptn["case_study"]["kind"],ptn["case_study"]["project"],ptn["case_study"]["title"]," | ".join(ref["url"] for ref in ptn["case_study"]["references"])," | ".join(ptn["sources"])])
    (WORK/"research"/"pattern-layer-mapping.csv").write_text(buf.getvalue(),encoding="utf-8")
    (WORK/"research"/"citation-register.json").write_text(json.dumps(SOURCES,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (WORK/"design"/"visual-grammar.md").write_text(f'''# Visual Grammar

- Canvas: 1200 × 675, 16:9, fixed light editorial theme.
- Human: ellipse, terracotta.
- Agent: clipped hexagon, blue.
- Workflow: rectangular process, teal.
- Model: capsule, violet.
- Tool: rounded capsule, ochre.
- Memory/state: cylinder, violet.
- Policy/guardrail: shield, red.
- External system/input: neutral rectangle.
- Solid dark arrow: control or delegation.
- Blue arrow: data/context.
- Violet dashed arrow: asynchronous message.
- Terracotta dashed arrow: feedback/revision/escalation.
- Every SVG retains text as text, includes title/desc, and carries a compact source footer.
- On narrow screens, each 16:9 pattern diagram is viewed through a 1040px-wide, keyboard-focusable internal viewport rather than being crushed to phone width.
''',encoding="utf-8")
    (WORK/"design"/"article-outline.md").write_text(f'''# Public Edition Information Architecture

## index.html — Blog narrative

1. The impossible four-way choice: ReAct / Multi-Agent / RAG / MCP
2. Three Pattern levels plus an independent Enablers catalog
3. Enterprise exception-handling example across L1–L3 and Enablers
4. {len(ANCHOR_IDS)} anchor patterns
5. {len(COMPARISONS)} comparison matrices
6. Four decision questions and trade-offs
7. Conclusion, method, provenance and selected sources

## atlas.html — complete reference layer

1. Search, layer filter and {len(PATTERNS)}-item directory
2. Atomic Common Patterns with direct, one-level Variants
3. Compound Patterns grouped separately at the end of each Level
4. L1 Agentic Application
5. L1 human–Agent qualitative map
6. L2 Agentic System
7. L3 Agentic Design Pattern
8. Techniques, Protocols & Practices as unnumbered Enablers
9. Trade-offs and 21-chapter coverage matrix
10. Method, provenance and complete reference index

## taxonomy.html — orthogonal classification browser

1. Search, Level / Enabler filter and {len(TAXONOMY_GROUPS)}-group taxonomy selector
2. Three-Level Pattern and Enabler taxonomy overview
3. Grouped Pattern index linking back to complete atlas entries
4. No changes to atlas directory order or Common/Variant/Compound hierarchy
''',encoding="utf-8")
    b2=io.StringIO();w2=csv.writer(b2);w2.writerow(["file","pattern_id","layer","topology","source_caption"])
    for ptn in PATTERNS:w2.writerow([f'diagrams/{ptn["id"]}.svg',ptn["id"],ptn["layer"],ptn["topology"],source_caption(ptn)])
    w2.writerow(["diagrams/three-level-pattern-map.svg","overview","ALL","three-pattern-level-map","article taxonomy"]);w2.writerow(["diagrams/visual-legend.svg","legend","ALL","legend","visual grammar"]);w2.writerow(["diagrams/enterprise-exception-case.svg","case-study","ALL","three-level-plus-enablers-case","article synthesis"]);w2.writerow(["diagrams/l1-human-agent-relative-map.svg","l1-relative-map","L1","qualitative-two-axis-map","article synthesis"])
    (WORK/"design"/"diagram-inventory.csv").write_text(b2.getvalue(),encoding="utf-8")


def build_outputs():
    DIAGRAMS.mkdir(parents=True,exist_ok=True);ASSETS.mkdir(parents=True,exist_ok=True);DATA.mkdir(parents=True,exist_ok=True)
    for ptn in PATTERNS:(DIAGRAMS/f'{ptn["id"]}.svg').write_text(render_svg(ptn),encoding="utf-8")
    (DIAGRAMS/"three-level-pattern-map.svg").write_text(render_layer_map(),encoding="utf-8")
    (DIAGRAMS/"visual-legend.svg").write_text(render_legend(),encoding="utf-8")
    (DIAGRAMS/"enterprise-exception-case.svg").write_text(render_case_study_svg(),encoding="utf-8")
    (DIAGRAMS/"l1-human-agent-relative-map.svg").write_text(render_l1_relative_map(),encoding="utf-8")
    social_svg = ASSETS/"social-card.svg"
    social_svg.write_text(render_social_card_svg(),encoding="utf-8")
    favicon = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="8" fill="{PALETTE['ink']}"/><rect x="8" y="8" width="12" height="48" fill="{LAYER_META['L1']['color']}"/><rect x="22" y="8" width="12" height="48" fill="{LAYER_META['L2']['color']}"/><rect x="36" y="8" width="12" height="48" fill="{LAYER_META['L3']['color']}"/><rect x="51" y="8" width="5" height="48" fill="none" stroke="{ENABLER_META['color']}" stroke-width="2"/></svg>'''
    (ASSETS/"favicon.svg").write_text(favicon,encoding="utf-8")
    (ASSETS/"article.css").write_text(CSS+"\n",encoding="utf-8")
    (ASSETS/"atlas.js").write_text(ATLAS_JS+"\n",encoding="utf-8")
    (ASSETS/"taxonomy.js").write_text(TAXONOMY_JS+"\n",encoding="utf-8")
    public_sources = {sid:{k:(public_locator(v) if k == "locator" else v) for k,v in source.items() if k != "pdf"} for sid,source in SOURCES.items()}
    public_patterns = copy.deepcopy(PATTERNS)
    for pattern in public_patterns:
        pattern["source_locators"] = {
            sid: public_locator(locator)
            for sid, locator in pattern.get("source_locators", {}).items()
        }
    catalog={
        "schema_version":"2.0",
        "title":BLOG["title"],
        "description":BLOG["description"],
        "author":BLOG["author"],
        "version":BLOG["version"],
        "date_published":BLOG["published"],
        "date_modified":BLOG["modified"],
        "sources_reviewed_through":ACCESSED_AT,
        "method_note":"本文借鉴 ISO/IEC/IEEE 42010:2022 对 Entity of Interest 与架构描述的区分；L1 至 L3 Pattern 层级与独立 Enablers 目录均为本文综合。适用信号、权衡、边界与跨层影响属于本文分析。",
        "rights":"© 2026 " + BLOG["author"] + ". All rights reserved.",
        "public_base_url":os.environ.get("ATLAS_PUBLIC_BASE_URL") or None,
        "suggested_citation":f'{BLOG["author"]}. 《{BLOG["title"]}》, version {BLOG["version"]}, {BLOG["published"]}.',
        "layers":LAYER_META,
        "enablers":ENABLER_META,
        "taxonomy_groups":TAXONOMY_GROUPS,
        "patterns":public_patterns,
        "sources":public_sources,
        "coverage":{"book_chapters":21,"entries":len(PATTERNS),"patterns":sum(p["catalog_type"] == "pattern" for p in PATTERNS),"enablers":sum(p["catalog_type"] == "enabler" for p in PATTERNS),"entry_diagrams":len(PATTERNS),"all_diagrams":len(PATTERNS)+4,"synthesis_diagrams":1,"case_studies":len(PATTERNS),"evidenced_case_studies":sum(p["case_study"]["kind"] != "说明性案例" for p in PATTERNS),"common_patterns":sum(p["organization_role"] == "common" for p in PATTERNS),"direct_variants":sum(p["organization_role"] == "variant" for p in PATTERNS),"compound_patterns":sum(p["organization_role"] == "compound" for p in PATTERNS),"taxonomy_groups":len(TAXONOMY_GROUPS)},
    }
    (DATA/"pattern-catalog.json").write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    blog=render_blog();atlas=render_atlas_page();taxonomy=render_taxonomy_page()
    (OUTPUT/"index.html").write_text(blog,encoding="utf-8")
    (OUTPUT/"atlas.html").write_text(atlas,encoding="utf-8")
    (OUTPUT/"taxonomy.html").write_text(taxonomy,encoding="utf-8")
    (OUTPUT/"agentic-pattern-blog-standalone.html").write_text(inline_document(blog),encoding="utf-8")
    (OUTPUT/"agentic-pattern-atlas-standalone.html").write_text(inline_document(atlas,script_name="atlas.js",atlas_standalone=True),encoding="utf-8")
    (OUTPUT/"agentic-pattern-taxonomy-standalone.html").write_text(inline_document(taxonomy,script_name="taxonomy.js",taxonomy_standalone=True),encoding="utf-8")


def build_qa():
    book_coverage={n:[] for n,_,_,_ in CHAPTERS}
    for ptn in PATTERNS:
        for n in book_coverage:
            if ptn.get("book_chapter")==n or f"adp-{n}" in ptn["sources"]:book_coverage[n].append(ptn["id"])
    missing=[n for n,ids in book_coverage.items() if not ids]
    missing_citations=[p["id"] for p in PATTERNS if not p["sources"]]
    schmid=[p["id"] for p in PATTERNS if "schmid-subagents" in p["sources"]]
    case_studies=[p["id"] for p in PATTERNS if p.get("case_study")]
    evidenced_cases=[p["id"] for p in PATTERNS if p.get("case_study", {}).get("kind") != "说明性案例"]
    common_patterns=[p["id"] for p in PATTERNS if p["organization_role"] == "common"]
    direct_variants=[p["id"] for p in PATTERNS if p["organization_role"] == "variant"]
    compound_patterns=[p["id"] for p in PATTERNS if p["organization_role"] == "compound"]
    coverage=f'''# Coverage Report

- Atlas entries (architecture, design, mechanism, protocol and technique): {len(PATTERNS)}
- Independent SVGs: {len(PATTERNS)+4}
- Text case studies: {len(case_studies)}/{len(PATTERNS)}
- Cases backed by a product, open-source project, official implementation, pattern example, or research prototype: {len(evidenced_cases)}/{len(PATTERNS)}
- Atomic Common Patterns: {len(common_patterns)} ({", ".join(common_patterns)})
- Direct Variants: {len(direct_variants)} ({", ".join(direct_variants)})
- Compound Patterns: {len(compound_patterns)} ({", ".join(compound_patterns)})
- Orthogonal Taxonomy Groups: {len(TAXONOMY_GROUPS)}; every Pattern is assigned exactly once.
- Book chapters covered: {21-len(missing)}/21
- Missing book chapters: {missing or "none"}
- Schmid subagent patterns covered: {len(schmid)}/4 ({", ".join(schmid)})
- Appendix A techniques represented: 22 named techniques plus context engineering and ReAct cross-links.
- Patterns without sources: {missing_citations or "none"}

## Layer distribution

'''+"\n".join(f'- {layer}: {sum(p["layer"]==layer for p in PATTERNS)}' for layer in LAYER_META)+"\n"
    (WORK/"qa"/"coverage-report.md").write_text(coverage,encoding="utf-8")
    citation_lines=["# Citation and Provenance Audit","",f"Patterns checked: {len(PATTERNS)}",f"Patterns with at least one source: {sum(bool(p['sources']) for p in PATTERNS)}",f"Source-original names: {sum(p['provenance']=='来源原名' for p in PATTERNS)}",f"Normalized names: {sum(p['provenance']=='规范化命名' for p in PATTERNS)}",f"Article-derived patterns: {sum(p['provenance']=='本文归纳' for p in PATTERNS)}","","Public catalog excludes all local filesystem paths. Agentic Design Patterns citations use the official Springer DOI with chapter, appendix or section locators.","","## Per-pattern register",""]
    for ptn in PATTERNS:citation_lines.append(f'- `{ptn["id"]}` — **{ptn["provenance"]}** — '+", ".join(f'[{SOURCES[s]["title"]}]({SOURCES[s]["url"]})' for s in ptn["sources"]))
    (WORK/"qa"/"citation-audit.md").write_text("\n".join(citation_lines)+"\n",encoding="utf-8")


if __name__ == "__main__":
    # Publishing only renders into the ignored output directory. Research and QA
    # reports are an explicit authoring operation, never a build side effect.
    import argparse
    parser = argparse.ArgumentParser(description="Build the Agentic Pattern Atlas from source")
    parser.add_argument("--reports", action="store_true", help="Also refresh authoring research and QA reports")
    args = parser.parse_args()
    build_outputs()
    if args.reports:
        build_intermediates()
        build_qa()
    print(json.dumps({"patterns":len(PATTERNS),"svg_files":len(list(DIAGRAMS.glob('*.svg'))),"output":str(OUTPUT)},ensure_ascii=False))
