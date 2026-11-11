import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
const {chromium} = await import(process.env.PLAYWRIGHT_MODULE ?? 'playwright');
const here = path.dirname(fileURLToPath(import.meta.url));
const browser = await chromium.launch({headless: true, executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
const page = await browser.newPage({viewport: {width: 2400, height: 1260}});
const results = [], errors = [], requests = [];
page.on('pageerror', e => errors.push(e.message));
page.on('request', r => requests.push(r.url()));
const geometry = () => page.evaluate(() => {
  const v = document.querySelector('#diagram-viewport'), s = document.querySelector('#diagram-stage');
  const vr = v.getBoundingClientRect(), sr = s.getBoundingClientRect(), m = new DOMMatrix(getComputedStyle(s).transform);
  return {viewport: {x: vr.x, y: vr.y, width: vr.width, height: vr.height},
    stage: {x: sr.x, y: sr.y, width: sr.width, height: sr.height},
    zoom: m.a, x: m.e, y: m.f,
    anchorX: (v.clientWidth / 2 - m.e) / m.a, anchorY: (v.clientHeight / 2 - m.f) / m.a};
});
const near = (a, b, message) => assert(Math.abs(a - b) < 1, `${message}: ${a} vs ${b}`);
const centered = g => {
  near(g.stage.x + g.stage.width / 2, g.viewport.x + g.viewport.width / 2, 'horizontal center');
  near(g.stage.y + g.stage.height / 2, g.viewport.y + g.viewport.height / 2, 'vertical center');
};
const check = async (name, action) => {
  try { await action(); results.push({name, pass: true}); }
  catch (e) { results.push({name, pass: false, error: e.message}); }
};
const fit = () => page.locator('#fit-view').click();
try {
  await page.goto(pathToFileURL(path.resolve(here, '../api-testing-map.html')).href);
  await page.evaluate(() => document.fonts.ready);
  await check('larger desktop canvas retains a separate detail panel', async () => {
    const g = await geometry();
    assert(g.viewport.width >= 2050 && g.viewport.height >= 1160, 'canvas must reclaim width and height');
    const panel = await page.locator('#detail-panel').boundingBox();
    assert(panel.x >= g.viewport.x + g.viewport.width, 'panel must not cover canvas');
  });
  await check('Fit centers the complete stage even when horizontal spare space exceeds 280px', async () => {
    await fit(); const g = await geometry(); centered(g);
    assert(g.stage.width < g.viewport.width && g.stage.height < g.viewport.height);
  });
  await check('Fit follows a small-to-large window resize', async () => {
    await page.setViewportSize({width: 1280, height: 720}); await fit(); const small = await geometry();
    await page.setViewportSize({width: 2400, height: 1260}); await page.waitForTimeout(100);
    const large = await geometry(); centered(large); assert(large.zoom > small.zoom + 0.1, 'Fit must recalculate scale');
  });
  await check('Command drag works in both directions from blank viewport outside the stage', async () => {
    await fit(); const before = await geometry();
    const x = before.viewport.x + before.viewport.width - 60, y = before.viewport.y + before.viewport.height / 2;
    assert(x > before.stage.x + before.stage.width, 'start must be outside paper');
    await page.mouse.move(x, y); await page.keyboard.down('Meta'); await page.mouse.down();
    await page.mouse.move(x - 60, y - 30, {steps: 4}); const first = await geometry();
    near(first.x, before.x - 60, 'left pan'); near(first.y, before.y - 30, 'up pan');
    await page.mouse.move(x + 40, y + 30, {steps: 4}); const second = await geometry();
    near(second.x, before.x + 40, 'right pan'); near(second.y, before.y + 30, 'down pan');
    await page.mouse.up(); await page.keyboard.up('Meta');
    assert.equal(await page.locator('#diagram-viewport.is-panning').count(), 0);
  });
  await page.mouse.up(); await page.keyboard.up('Meta');
  await check('Right drag starts in blank viewport and simple right click leaves view unchanged', async () => {
    await fit(); const before = await geometry();
    const x = before.viewport.width - 45, y = before.viewport.y + 140;
    await page.mouse.move(x, y); await page.mouse.down({button: 'right'});
    await page.mouse.move(x - 50, y + 40, {steps: 4}); await page.mouse.up({button: 'right'});
    const after = await geometry(); near(after.x, before.x - 50, 'right drag x'); near(after.y, before.y + 40, 'right drag y');
    await page.mouse.click(x, y, {button: 'right'}); const clicked = await geometry();
    near(clicked.x, after.x, 'simple right click x'); near(clicked.y, after.y, 'simple right click y');
  });
  await check('manual zoom preserves scale and viewport-center diagram point on resize', async () => {
    await page.setViewportSize({width: 1600, height: 1000}); await page.locator('#reset-view').click();
    await page.locator('#zoom-in').click(); const before = await geometry();
    await page.setViewportSize({width: 2000, height: 1100}); await page.waitForTimeout(100);
    const after = await geometry(); near(after.zoom, before.zoom, 'manual scale');
    near(after.anchorX, before.anchorX, 'manual center anchor x'); near(after.anchorY, before.anchorY, 'manual center anchor y');
  });
  await check('unmodified drag, Ctrl click and excluded node buttons never begin pan', async () => {
    await page.setViewportSize({width: 2400, height: 1260}); await fit();
    const before = await geometry(), x = before.viewport.width - 60, y = before.viewport.y + 150;
    await page.mouse.move(x, y); await page.mouse.down(); await page.mouse.move(x - 70, y + 10); await page.mouse.up();
    const after = await geometry(); near(after.x, before.x, 'plain drag x'); near(after.y, before.y, 'plain drag y');
    await page.keyboard.down('Control'); await page.mouse.down();
    assert.equal(await page.locator('#diagram-viewport.is-panning').count(), 0); await page.mouse.up(); await page.keyboard.up('Control');
    const button = await page.locator('#node-S01 > header button').first().boundingBox();
    await page.keyboard.down('Meta'); await page.mouse.move(button.x + 10, button.y + 10); await page.mouse.down();
    assert.equal(await page.locator('#diagram-viewport.is-panning').count(), 0); await page.mouse.up(); await page.keyboard.up('Meta');
  });
  await check('mobile canvas stays above the panel and fits after resize', async () => {
    await page.setViewportSize({width: 720, height: 1000}); await fit(); const g = await geometry(); centered(g);
    const panel = await page.locator('#detail-panel').boundingBox(); assert(panel.y >= g.viewport.y + g.viewport.height);
  });
  await page.setViewportSize({width: 2400, height: 1260}); await fit();
  const final = await geometry();
  if (!process.argv.includes('--red')) await page.screenshot({path: path.join(here, 'qa/map-wide-centered.png')});
  assert.deepEqual(errors, []); assert(!requests.some(u => /^https?:/.test(u)), 'no external requests');
  const report = {results, geometry: final, errors, externalRequests: 0, physicalMouseTest: false};
  fs.writeFileSync(path.join(here, 'qa', process.argv.includes('--red') ? 'canvas-layout-red.json' : 'canvas-layout-qa.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify(report, null, 2));
  assert(results.every(r => r.pass), 'canvas regression checks failed');
} finally { await browser.close(); }
