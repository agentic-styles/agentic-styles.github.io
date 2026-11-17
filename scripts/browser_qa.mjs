import { chromium } from 'playwright';
import http from 'node:http';
import { readFile, mkdir, writeFile, stat } from 'node:fs/promises';
import { resolve, extname, join, sep } from 'node:path';
import { execFileSync } from 'node:child_process';

const root = resolve('dist');
const qa = resolve('.qa');
await mkdir(qa, { recursive: true });
const mime = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.png': 'image/png', '.json': 'application/json', '.pdf': 'application/pdf', '.md': 'text/plain; charset=utf-8' };
const server = http.createServer(async (request, response) => {
  try {
    const url = new URL(request.url, 'http://localhost');
    let path = resolve(root, decodeURIComponent(url.pathname.slice(1)));
    if (path !== root && !path.startsWith(root + sep)) { response.writeHead(403).end(); return; }
    if ((await stat(path)).isDirectory()) path = join(path, 'index.html');
    response.writeHead(200, { 'Content-Type': mime[extname(path)] || 'application/octet-stream' });
    response.end(await readFile(path));
  } catch { response.writeHead(404).end('Not found'); }
});
await new Promise((resolve, reject) => {
  server.once('error', reject);
  server.listen(0, '127.0.0.1', resolve);
});
const base = `http://127.0.0.1:${server.address().port}/`;
const browser = await chromium.launch({ headless: true, ...(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {}) });
const report = { checks: [], consoleErrors: [], failedRequests: [] };
const assert = (name, pass, actual) => {
  report.checks.push({ name, pass, actual });
  if (!pass) throw new Error(`${name}: ${JSON.stringify(actual)}`);
};

async function pageAt(path) {
  const page = await browser.newPage({ viewport: { width: 1600, height: 900 } });
  page.on('pageerror', error => report.consoleErrors.push({ path, error: error.message }));
  page.on('response', response => {
    if (response.status() >= 400) report.failedRequests.push({ path, url: response.url(), status: response.status() });
  });
  const response = await page.goto(base + path, { waitUntil: 'networkidle' });
  assert(`${path} HTTP`, response.status() === 200, response.status());
  await page.evaluate(() => document.fonts.ready);
  return page;
}

try {
  for (const path of ['', 'atlas/', 'atlas/atlas.html', 'atlas/taxonomy.html', 'lab/tutorial.html']) {
    const page = await pageAt(path);
    const broken = await page.locator('img').evaluateAll(images => images.filter(image => !image.complete || image.naturalWidth === 0).map(image => image.src));
    assert(`${path} images`, broken.length === 0, broken);
    if (path === 'atlas/atlas.html') {
      assert('Atlas entries', await page.locator('.pattern-entry').count() === 55, await page.locator('.pattern-entry').count());
      await page.locator('[data-pattern-search]').fill('Supervisor');
      const filtered = await page.locator('.pattern-entry:not([hidden])').count();
      assert('Atlas search reduces entries', filtered > 0 && filtered < 55, filtered);
      await page.locator('[data-pattern-search]').fill('no-such-pattern-qa-928374');
      assert('Atlas search zero match', await page.locator('.pattern-entry:not([hidden])').count() === 0, await page.locator('.pattern-entry:not([hidden])').count());
      await page.locator('[data-pattern-search]').fill('');
      assert('Atlas clear restores entries', await page.locator('.pattern-entry:not([hidden])').count() === 55, await page.locator('.pattern-entry:not([hidden])').count());
    }
    await page.screenshot({ path: join(qa, (path.replaceAll('/', '-') || 'home') + '.png') });
    await page.close();
  }
  for (const [directory, expected] of [['course', 64], ['lab', 71]]) {
    const page = await pageAt(`${directory}/presentation.html`);
    assert(`${directory} slide count`, await page.locator('.slide').count() === expected, await page.locator('.slide').count());
    const first = await page.locator('.slide.active').getAttribute('data-id') ?? await page.locator('.slide.active').getAttribute('data-title');
    await page.keyboard.press('ArrowRight');
    const second = await page.locator('.slide.active').getAttribute('data-id') ?? await page.locator('.slide.active').getAttribute('data-title');
    assert(`${directory} keyboard navigation`, first !== second, { first, second });
    await page.keyboard.press('Home');
    const broken = await page.locator('img').evaluateAll(images => images.filter(image => !image.complete || image.naturalWidth === 0).map(image => image.src));
    assert(`${directory} images`, broken.length === 0, broken);
    await page.screenshot({ path: join(qa, `${directory}-first.png`) });
    await page.emulateMedia({ media: 'print' });
    await page.addStyleTag({ content: '@page{size:13.333333in 7.5in;margin:0}.slide:last-child{break-after:auto!important;page-break-after:auto!important}' });
    const pdf = join(root, directory, `${directory}.pdf`);
    await page.pdf({ path: pdf, printBackground: true, preferCSSPageSize: true, margin: { top: '0', right: '0', bottom: '0', left: '0' } });
    const info = execFileSync(process.env.PDFINFO_PATH || 'pdfinfo', [pdf], { encoding: 'utf8' });
    const pages = Number(info.match(/^Pages:\s+(\d+)/m)?.[1]);
    assert(`${directory} PDF pages`, pages === expected, pages);
    const size = info.match(/^Page size:\s+([\d.]+) x ([\d.]+)/m);
    assert(`${directory} PDF dimensions`, size && Math.abs(Number(size[1]) - 960) < 1 && Math.abs(Number(size[2]) - 540) < 1, size?.slice(1));
    await page.close();
  }
  assert('No browser runtime errors', report.consoleErrors.length === 0, report.consoleErrors);
  assert('No failed page assets', report.failedRequests.length === 0, report.failedRequests);
} finally {
  await writeFile(join(qa, 'report.json'), JSON.stringify(report, null, 2) + '\n');
  await browser.close();
  await new Promise(resolve => server.close(resolve));
}
console.log(`PASS: ${report.checks.length} browser/PDF checks`);
