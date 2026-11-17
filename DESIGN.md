---
name: Agentic Pattern Atlas
description: 一份以结构证据、三层 Pattern 语义、独立实现手段目录和可引用来源组织 Agentic Architecture 的视觉现场手册。
colors:
  warm-paper: "#f4f0e7"
  clear-paper: "#fbf8f1"
  deep-ink: "#172331"
  annotation-slate: "#5a6671"
  quiet-rule: "#c8c4bb"
  field-note: "#e9e4da"
  decision-wash: "#e5dfd2"
  l1-responsibility: "#b5472d"
  l2-orchestration: "#1c6e67"
  l3-cognition: "#315ea8"
  implementation-enabler: "#896b24"
  focus-amber: "#d88b43"
typography:
  display:
    fontFamily: "Iowan Old Style, Songti SC, STSong, serif"
    fontSize: "clamp(3.5rem, 7vw, 8rem)"
    fontWeight: 700
    lineHeight: 0.98
    letterSpacing: "-0.055em"
  headline:
    fontFamily: "Iowan Old Style, Songti SC, STSong, serif"
    fontSize: "clamp(2.5rem, 5vw, 5.2rem)"
    fontWeight: 700
    lineHeight: 1.04
    letterSpacing: "-0.04em"
  title:
    fontFamily: "Iowan Old Style, Songti SC, STSong, serif"
    fontSize: "clamp(1.7rem, 3vw, 2.8rem)"
    fontWeight: 700
    lineHeight: 1.1
  body:
    fontFamily: "Avenir Next, PingFang SC, Microsoft YaHei, sans-serif"
    fontSize: "clamp(16px, 1.25vw, 19px)"
    fontWeight: 400
    lineHeight: 1.7
  label:
    fontFamily: "Avenir Next, PingFang SC, Microsoft YaHei, sans-serif"
    fontSize: "0.68rem"
    fontWeight: 800
    lineHeight: 1.35
    letterSpacing: "0.12em"
rounded:
  square: "0"
spacing:
  xs: "0.35rem"
  sm: "0.55rem"
  md: "1rem"
  lg: "1.3rem"
  xl: "2rem"
  section: "clamp(4rem, 8vw, 8rem)"
components:
  filter-button:
    backgroundColor: "{colors.clear-paper}"
    textColor: "{colors.deep-ink}"
    typography: "{typography.label}"
    rounded: "{rounded.square}"
    padding: "0.55rem 0.7rem"
  filter-button-selected:
    backgroundColor: "{colors.deep-ink}"
    textColor: "{colors.clear-paper}"
    typography: "{typography.label}"
    rounded: "{rounded.square}"
    padding: "0.55rem 0.7rem"
  search-field:
    backgroundColor: "{colors.warm-paper}"
    textColor: "{colors.deep-ink}"
    typography: "{typography.body}"
    rounded: "{rounded.square}"
    padding: "0.75rem 0.9rem"
    height: "2.8rem"
  taxonomy-badge:
    backgroundColor: "{colors.clear-paper}"
    textColor: "{colors.deep-ink}"
    typography: "{typography.label}"
    rounded: "{rounded.square}"
    padding: "0.3rem 0.55rem"
  navigation:
    backgroundColor: "{colors.deep-ink}"
    textColor: "{colors.clear-paper}"
    typography: "{typography.label}"
    rounded: "{rounded.square}"
    height: "4rem"
---

# Design System: Agentic Pattern Atlas

## 1. Overview

**Creative North Star: "架构现场手册"**

这套设计像一本在架构评审现场摊开的技术手册：暖纸承载长时间阅读，深墨建立判断的重量，色彩只在需要区分 System of Interest 或关系语义时出现。它的气质是严谨、清醒、具象；结构证据先于装饰，批注和索引先于营销话术。

页面以严格网格、非对称比例、细规则和大幅留白组织密集内容。桌面端服务 16:9 课程讲解，窄屏通过重排与局部横向浏览保留拓扑细节，打印版必须保留内容、案例和来源。系统明确拒绝通用 SaaS 卡片墙、霓虹 AI 视觉、渐变、玻璃拟态，以及只画箭头却不表达控制权和责任边界的伪架构图。

**Key Characteristics:**

- 暖纸、深墨、低饱和三层 Pattern 信号色与独立的实现手段标识。
- Serif 承担概念与判断，Sans 承担说明、索引和控制。
- 以规则线、色块和空间层级取代阴影。
- 图形同时编码控制、数据、异步与反馈，颜色从不单独承担含义。
- 导航、筛选、窄屏和打印都属于核心体验，不是附加适配。

## 2. Colors

这是一套被纸张和油墨约束的全色板：中性色占据大部分表面，L1 至 L3 色彩只承担 Pattern 层级语义；赭金标识独立的实现手段目录，焦点琥珀只用于键盘可见性。

### Primary

- **深墨蓝黑** (#172331): 正文、规则线、主导航与深色章节的结构骨架，对应 `deep-ink`。
- **暖编辑纸** (#f4f0e7): 页面主背景，降低长时间阅读时的眩光，对应 `warm-paper`。
- **清晰纸白** (#fbf8f1): 图表底、输入控件和交替内容面的轻微提亮，对应 `clear-paper`。

### Secondary

- **L1 责任陶土** (#b5472d): 业务责任、人机关系与 Application 层，对应 `l1-responsibility`。
- **L2 编排青绿** (#1c6e67): 系统控制权、委派与 Orchestration 层，对应 `l2-orchestration`。
- **L3 设计蓝** (#315ea8): Agent 决策、行动与局部控制结构等 Design Pattern，对应 `l3-cognition`。
- **实现手段赭金** (#896b24): Technique、Protocol、Practice 与 Capability Format 的独立目录标识，对应 `implementation-enabler`；它不是第四层 Pattern。

### Tertiary

- **焦点琥珀** (#d88b43): 仅用于 `:focus-visible` 的高对比轮廓，不作为品牌装饰，对应 `focus-amber`。

### Neutral

- **批注灰** (#5a6671): 次要说明、英文副标题、图注和元数据，对应 `annotation-slate`。
- **安静规则** (#c8c4bb): 表格、目录、分组和图框的 1px 分隔线，对应 `quiet-rule`。
- **现场笔记纸** (#e9e4da): 案例、分类概览和需要聚合阅读的次级表面，对应 `field-note`。
- **决策淡纸** (#e5dfd2): 权衡、方法声明和 Compound 关系说明的强调表面，对应 `decision-wash`。

### Named Rules

**The Semantic Color Rule.** L1 至 L3 色彩必须回答“当前是哪个 System of Interest”；赭金只回答“这是实现手段而非 Pattern”，禁止用于无语义装饰。

**The Ink and Paper Rule.** 任一常规页面都应由暖纸和深墨主导；如果信号色占据大多数内容面，说明颜色已经越权。

## 3. Typography

**Display Font:** Iowan Old Style，中文回退为 Songti SC / STSong
**Body Font:** Avenir Next，中文回退为 PingFang SC / Microsoft YaHei

**Character:** Serif 像架构论证中的结论和章节标记，具有编辑重量；Sans 像图纸批注和索引，清晰、克制、适合持续扫描。二者共同形成“概念有声量，证据不喧哗”的阅读节奏。

### Hierarchy

- **Display** (weight 700, fluid 3.5rem to 8rem, line-height 0.98): 只用于 Hero、Level 编号和单一强结论；紧缩字距制造版面张力。
- **Headline** (weight 700, fluid 2.5rem to 5.2rem, line-height 1.04): 章节标题、Pattern 名称和分类组标题。
- **Title** (weight 700, fluid 1.7rem to 2.8rem, line-height 1.1): 案例标题、局部模块标题和重要索引名。
- **Body** (weight 400, fluid 16px to 19px, line-height 1.7): 解释、适用信号、权衡和案例正文；连续文本限制在约 65 至 75 个字符宽度。
- **Label** (weight 800, 0.68rem, letter-spacing 0.12em): Level、来源、Pattern 角色和短控制标签；只对短标签使用大写。

### Named Rules

**The Two Voices Rule.** Serif 负责“这是什么与为何重要”，Sans 负责“如何读、如何找与如何操作”；禁止用展示字体承载长段正文。

**The Screen Share Rule.** 任何关键结论在 16:9 共享屏幕上都必须一眼可读；缩小字号不能作为解决信息过载的手段。

## 4. Elevation

系统采用结构化平面，不使用常规投影。深度由纸张色阶、1px 或 2px 规则、章节色块、交替背景和留白节奏表达；唯一近似阴影的效果是 Hero 中的装饰性同心线，它不表示可交互层级。

### Named Rules

**The Structural Flatness Rule.** 静止表面必须保持平面；需要强调时使用完整背景、规则线或空间分隔，禁止用悬浮阴影伪造层级。

**The Rule Weight Rule.** 1px 表示分隔，2px 表示章节或组的开始，3px 只用于键盘焦点或极少数 Pattern 证据线。

## 5. Components

组件应像现场手册中的索引、批注和控制工具：边界清楚、直角、低装饰，状态变化必须可见且不改变版面结构。

### Buttons

- **Shape:** 严格直角（0 radius），以细边框定义点击区域。
- **Primary:** 深墨背景配清晰纸白文字；主要用于当前筛选状态和高优先级行动。
- **Hover / Focus:** Hover 通过边框或文字对比增强；键盘焦点统一使用 3px 焦点琥珀轮廓并向外偏移 4px。
- **Secondary / Ghost:** 透明或清晰纸背景配安静规则边框；选中后反转为深墨底。

### Chips

- **Style:** Taxonomy badge 与技术标签使用清晰纸背景、1px 安静规则边框和紧凑 Sans 标签。
- **State:** Badge 是导航线索，不是彩色状态胶囊；Hover 只加深边框，禁止圆角和彩色填充泛滥。

### Cards / Containers

- **Corner Style:** 直角，不使用统一圆角卡片模板。
- **Background:** 使用暖编辑纸、清晰纸白、现场笔记纸或决策淡纸形成语义层次。
- **Shadow Strategy:** 无阴影；遵循 Structural Flatness Rule。
- **Border:** 以完整的 1px 分隔线和 2px 起始规则组织内容。
- **Internal Padding:** 紧凑索引约 0.55rem 至 1rem，正文型案例约 1.3rem 至 2.5rem。

### Inputs / Fields

- **Style:** 暖编辑纸背景、深墨文字、1px 深墨边框、严格直角；高度至少 2.8rem。
- **Focus:** 使用统一的 3px 焦点琥珀外轮廓，不通过阴影发光。
- **Error / Disabled:** 当前图鉴没有独立错误态；新增时必须同时提供文字说明和非颜色编码。

### Navigation

- **Style:** Sticky 深墨导航承载站点标识与文本链接；当前页面用下划线和纸白文字双重表达，不只依赖颜色。
- **Mobile:** 在 560px 以下切换为两行网格，链接左对齐并允许换行；不得挤压站点标识。

### Pattern Entry

Pattern Entry 是签名组件。顶部 Kicker 先给出 L1–L3 Level 或 ENABLER、类型、来源归属和序号；Pattern 可选 Taxonomy badge 与 Common / Variant / Compound 关系条，Enabler 则以 Technique / Protocol / Practice 类型出现；概念标题与意图形成非对称双栏；拓扑图、适用信号、代价、结构说明、案例和来源按证据强度依次展开。窄屏将文字区域重排为单列，但拓扑保留至少 1040px 的内部画布并提供键盘可达的横向浏览。

## 6. Do's and Don'ts

### Do:

- **Do** 先用 Level、责任、控制、状态和关系语义建立结构，再添加 Pattern 名称。
- **Do** 使用暖编辑纸、清晰纸白和深墨作为主要阅读表面，并把 L1 至 L3 色彩限制在 Pattern 层级语义中，把赭金限制在实现手段标识中。
- **Do** 让来源原名、规范化命名和本文归纳在视觉上可区分。
- **Do** 为图形提供可搜索文字、标题、描述和替代文本，并同时使用线型、标签与颜色表达关系。
- **Do** 保持键盘焦点、窄屏横向拓扑、打印版和离线版内容完整。
- **Do** 用留白和规则线分组；1px 用于分隔，2px 用于明确开始。

### Don't:

- **Don't** 使用“通用 SaaS 卡片墙和重复的图标、标题、说明模板”。
- **Don't** 使用“霓虹、渐变、玻璃拟态等缺乏架构语义的 AI 感装饰”。
- **Don't** 把 Protocol、Technology 或 Prompt Technique 冒充 Architecture Pattern。
- **Don't** 只画箭头却不说明控制权、状态、责任和终止条件。
- **Don't** 为追求信息密度而牺牲窄屏、打印、键盘浏览或文字可读性。
- **Don't** 使用大于 1px 的彩色左侧或右侧条纹作为卡片强调；使用完整背景、规则线或编号。
- **Don't** 用阴影、圆角胶囊和动效制造不具备语义的层级。
