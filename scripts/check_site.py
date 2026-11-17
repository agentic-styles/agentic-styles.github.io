"""Check built-site links and reject generated artifacts in reachable Git history."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def historical_artifacts(repository: Path) -> list[str]:
    """Inspect paths in every historical tree, including aliases of one blob."""
    trees = subprocess.check_output(['git', 'log', '--all', '--format=%T'], cwd=repository, text=True).splitlines()
    bad = set()
    forbidden = ('dist/', 'outputs/', '.qa/', 'work/qa/', 'work/research/', 'work/design/', 'node_modules/')
    for tree in set(trees):
        paths = subprocess.check_output(['git', 'ls-tree', '-rz', '--name-only', tree], cwd=repository).decode().split('\0')
        for name in paths:
            if name and (Path(name).suffix.lower() in {'.html', '.htm', '.pdf'} or name.startswith(forbidden)):
                bad.add(name)
    return sorted(bad)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ('href', 'src') and value:
                self.links.append(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', type=Path, default=ROOT / 'dist')
    parser.add_argument('--skip-history', action='store_true')
    parser.add_argument('--before-pdf', action='store_true')
    args = parser.parse_args()
    site = args.site.resolve()
    errors = []
    pages = list(site.rglob('*.html'))
    for page in pages:
        text = page.read_text(encoding='utf-8')
        if re.search(r'(?:/Users/|/home/|file://|raw\.githack\.com/canmor/)', text):
            errors.append(f'{page.relative_to(site)}: private path or obsolete hosting link')
        links = Links()
        links.feed(text)
        for value in links.links:
            url = urlsplit(value)
            if url.scheme or url.netloc or not url.path:
                continue
            path = unquote(url.path)
            if args.before_pdf and path.endswith('.pdf'):
                continue
            if path.startswith('/patterns/'):
                target = site / path.removeprefix('/patterns/')
            elif path.startswith('/'):
                errors.append(f'{page.relative_to(site)}: non-portable root link {value}')
                continue
            else:
                target = page.parent / path
            if target.is_dir():
                target = target / 'index.html'
            if not target.is_file():
                errors.append(f'{page.relative_to(site)}: missing {value}')
    if not args.skip_history:
        errors.extend(f'Generated artifact in Git history: {name}' for name in historical_artifacts(ROOT))
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'PASS: {len(pages)} built HTML pages, local links and source-only Git policy')


if __name__ == '__main__':
    main()
