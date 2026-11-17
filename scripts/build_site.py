"""Build the public site from source; all generated files stay in dist/."""
from pathlib import Path
import argparse
import os
import shutil

from build_patterns import build as build_patterns
from build_lab import build as build_lab

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    parser.add_argument('--base-url', default='https://agentic-styles.github.io/patterns/')
    args = parser.parse_args()
    output = args.output.resolve()
    if output == ROOT or output in ROOT.parents:
        parser.error('Output must not contain the source checkout')
    if ROOT in output.parents and output.relative_to(ROOT).parts[0] not in {'dist', '.qa'}:
        parser.error('Inside the checkout, output must be under dist/ or .qa/')
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    os.environ['ATLAS_PUBLIC_BASE_URL'] = args.base_url.rstrip('/') + '/atlas/'
    build_patterns(output)
    build_lab(output)
    (output / '.nojekyll').touch()
    (output / 'index.html').write_text('''<!doctype html>
<html lang="zh-Hans"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agentic Styles · Patterns</title><meta name="description" content="Agentic 系统的架构模式、设计方法与实验课程。">
<link rel="icon" href="atlas/assets/favicon.svg"><style>
:root{color-scheme:light}*{box-sizing:border-box}body{margin:0;background:#f4f0e7;color:#172331;font:18px/1.7 system-ui,sans-serif}
main{max-width:1040px;margin:auto;padding:72px 24px}small{letter-spacing:.12em}h1,h2{font-family:Georgia,"Songti SC",serif;line-height:1.15}h1{font-size:clamp(48px,8vw,88px);margin:20px 0}h2{font-size:30px}a{color:#1c6e67;text-underline-offset:5px}a:focus-visible{outline:3px solid #d88b43;outline-offset:5px}section{border-top:1px solid #c8c4bb;padding:24px 0}p{max-width:70ch}.links{display:flex;flex-wrap:wrap;gap:12px 28px}footer{border-top:1px solid #c8c4bb;margin-top:48px;padding-top:20px;font-size:15px}
</style></head><body><main><small>AGENTIC STYLES · ARCHITECTURE FIELD NOTES</small>
<h1>先看见结构，<br>再作出设计。</h1><p>面向 Agentic 系统的架构模式、设计方法与实验课程。从责任与控制边界出发，理解结构、比较权衡，并用证据检验设计。</p>
<section><h2>01 · 模式图鉴</h2><p>从业务责任、系统组织和局部控制结构三个层级浏览模式；技术、协议和工程实践独立编目。</p><div class="links"><a href="atlas/">阅读主线</a><a href="atlas/atlas.html">完整图鉴</a><a href="atlas/taxonomy.html">分类浏览</a><a href="atlas/data/pattern-catalog.json">模式数据</a></div></section>
<section><h2>02 · Pattern 基础课</h2><p>先确定 System of Interest，再区分 Pattern 层级、控制权和组合方式。</p><div class="links"><a href="course/">开始课程</a><a href="course/speaker-script.md">讲师稿</a><a href="course/course.pdf">下载 PDF</a></div></section>
<section><h2>03 · 架构实验课</h2><p>用合成订舱预审案例，练习从质量属性场景到架构假设、协作契约、对比实验和设计决定。本仓库提供课程；独立 Labs 提供教学基线、合成样本、契约与评分工具。首版验证限于离线规则与协议测试，不代表真实模型准确率，候选 Multi-Agent 方案仍需实现。</p><div class="links"><a href="lab/">开始实验课</a><a href="lab/tutorial.html">学习指南</a><a href="https://github.com/agentic-styles/labs/tree/v0.1.0/booking-precheck">实验工程 v0.1.0</a><a href="lab/lab.pdf">下载 PDF</a></div></section>
<footer><a href="https://github.com/agentic-styles/patterns">源码与贡献</a> · HTML、图表与 PDF 均由 GitHub Actions 构建并部署。</footer>
</main></body></html>''', encoding='utf-8')
    print(f'Built site: {output}')


if __name__ == '__main__':
    main()
