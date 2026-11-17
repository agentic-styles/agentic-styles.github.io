# Agentic Styles · Patterns

面向 Agentic 系统的架构模式、设计方法与权衡。以业务责任（L1）、系统组织（L2）和局部控制结构（L3）组织 Pattern，独立编目技术、协议与工程实践，并通过课程学习如何作出设计决定。

## 在线阅读

- [站点首页](https://agentic-styles.github.io/)
- [图鉴文章](https://agentic-styles.github.io/atlas/)
- [完整图鉴](https://agentic-styles.github.io/atlas/atlas.html)
- [分类浏览](https://agentic-styles.github.io/atlas/taxonomy.html)
- [Pattern 基础课](https://agentic-styles.github.io/course/)
- [架构实验课](https://agentic-styles.github.io/lab/)

基础课讲解模式、分类与组合；实验课通过合成 Booking Precheck 案例，练习质量属性场景、架构假设、协作契约与验证决定。本仓库只维护课程；独立的 [Labs 实验工程 v0.1.1](https://github.com/agentic-styles/labs/tree/v0.1.1/booking-precheck) 提供 Single-Agent 教学基线、合成样本、契约和评分工具。首版验证范围限于离线规则、协议与 scripted 工具循环测试，不代表真实 LLM 准确率，也未提供完成的 Multi-Agent 方案。课程示例指标不是本次迁移复跑的实验结论。

运行工程的环境准备与离线命令见 [实验课教程](docs/architecture-lab/tutorial.md)；网站构建不依赖 Labs，不会安装运行工程的依赖或把它作为 submodule。

## 源码结构

```text
work/*.py                 图鉴内容、模式数据与生成器
src/pattern-course/       基础课可编辑模板、CSS、JavaScript 与源素材
src/architecture-lab/     实验课可编辑模板、CSS 与 JavaScript
docs/architecture-lab/    教程、大纲与来源说明
scripts/                 构建、链接检查、浏览器检查与 PDF 导出
.github/workflows/        GitHub Actions → GitHub Pages
```

`.html.in` 是人工维护的课程源码模板，不是预生成页面。图鉴 HTML、SVG、JSON、standalone 文件、PDF、截图和 QA 报告在构建时生成；它们不进入 Git，也不创建 `gh-pages` 制品分支。

## 本地构建

构建网站只需要 Python 3.12+，不读取私有归档、本机书籍 PDF 或任何凭据：

```sh
git clone https://github.com/agentic-styles/agentic-styles.github.io.git
cd agentic-styles.github.io
python3 scripts/build_site.py
python3 -m http.server 8000 --directory dist
```

打开 http://localhost:8000/ 。构建输出位于忽略的 `dist/`，可以从仓库之外调用构建脚本。需要定制正式站点地址时使用 `--base-url`；默认是上述 GitHub Pages 地址。

浏览器检查及 PDF 导出需要 Node.js 24+、Playwright Chromium、Poppler 的 `pdfinfo` 以及可显示中文的字体：

```sh
npm ci
npx playwright install chromium
python3 scripts/check_site.py --before-pdf
npm run qa
python3 scripts/check_site.py
```

本机已有 Chrome 时可通过 `CHROME_PATH` 指定可执行文件。两个课程 PDF 分别生成于 `dist/course/course.pdf`（64 页）与 `dist/lab/lab.pdf`（71 页）；页面尺寸为 960 × 540 pt。报告和截图位于忽略的 `.qa/`。

## 发布与制品政策

推送到 `main` 或手动执行 **Build and deploy Pages** 会构建网站、检查本地链接与 Git 历史、运行浏览器检查、导出 PDF，再发布到 GitHub Pages。Pull Request 运行相同检查，但不部署。

Pages 的发布源为 **GitHub Actions**。部署仅上传 `dist/`，不会暴露研究目录、仓库配置、源码或私有归档。完整构建结果与 QA 报告也作为 Actions artifact 保留 14 天，PDF 可从线上站点下载。

首次迁移采用全新的源码提交；旧仓库历史不接入当前仓库。CI 检查所有可达提交，拒绝 `.html`、`.htm`、`.pdf` 及 `outputs/`、`dist/` 制品路径。后续更新也只能提交源码、模板和必要源素材。

## 内容来源与维护

- [产品定位](PRODUCT.md)
- [设计系统](DESIGN.md)
- [实验课来源与迁移边界](docs/architecture-lab/provenance.md)

图鉴的层级与术语综合属于本项目分析，不是统一行业标准；每个条目的原始来源与综合归属保存在内容数据中，并随构建输出公开。原 OOCL 项目的完整交付快照继续留在私有归档，本仓库只维护提取后的课程内容。
