import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
const {chromium} = await import(process.env.PLAYWRIGHT_MODULE ?? 'playwright');
const here = path.dirname(fileURLToPath(import.meta.url));
const browser = await chromium.launch({headless: true, executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
const page = await browser.newPage({viewport: {width: 1440, height: 1000}});
const results = [], errors = [], external = [], red = process.argv.includes('--red');
const requestReview = process.argv.includes('--requests');
const codeReview = process.argv.includes('--code');
page.on('pageerror', e => errors.push(e.message));
page.on('request', r => { if (/^https?:/.test(r.url())) external.push(r.url()); });
const check = async (id, fn) => {
  try { await fn(); results.push({id, pass: true}); }
  catch (e) { results.push({id, pass: false, error: e.message}); }
};
const openSuite = id => page.locator(`.jump-bar [data-focus="${id}"]`).click();
try {
  await page.goto(pathToFileURL(path.resolve(here, '../api-testing-map.html')).href);
  await page.evaluate(() => document.fonts.ready);
  const panel = page.locator('#detail-panel');
  for (const [sid, count] of [['S01', 7], ['S02', 3], ['S03', 5]]) {
    await openSuite(sid);
    await check(sid, async () => {
      if(requestReview){
        assert.equal(await panel.locator('[data-detail="base-choice"] [data-base-reason]').count(), sid==='S02'?1:2, `${sid} needs reasons for its base`);
        assert.match(await panel.locator('[data-detail="base-choice"]').textContent(), /ทำไมเลือก/);
      }
      assert.equal(await panel.locator('[data-detail="criterion"]').count(), 1, `${sid} criterion must be shown on click`);
      assert.match(await panel.locator('[data-detail="criterion"]').textContent(), /Base Choice Coverage/);
      assert.equal(await panel.locator('[data-detail="characteristics"] details').count(), 1);
      await panel.locator('[data-detail="characteristics"] summary').click();
      assert.match(await panel.locator('[data-detail="characteristics"]').textContent(), /Functionality-based/);
      assert.match(await panel.locator('[data-detail="criterion-count"]').textContent(), new RegExp(`= ${count}`));
      assert.equal(await panel.locator('[data-detail="suite-cases"] button').count(), count);
      await panel.locator('[data-detail="characteristics"] summary').click();
      if (!red) { await panel.evaluate(e => { e.scrollTop = 0; }); await page.screenshot({path: path.join(here, `qa/learning-${sid}.png`)}); }
    });
    for (let i = 1; i <= count; i++) {
      const cid = `${sid}-${String(i).padStart(2, '0')}`;
      await openSuite(sid);
      // Real click on the suite's child navigation, not calling the internal select API.
      await panel.locator(`.detail-buttons > [data-pick="${cid}"]`).click();
      await check(cid, async () => {
        if(codeReview){
          assert.equal(await panel.locator('[data-detail="example-code"]').count(),1,`${cid} needs visible example code`);
          const snippet=await panel.locator('[data-detail="example-code"] code').first().textContent();
          assert(snippet.includes(`def example_${cid.toLowerCase().replaceAll('-','_')}(api, products):`));
          assert.match(await panel.locator('[data-detail="example-code"]').textContent(),/fixtures/);
          const before=await page.locator('#diagram-stage').evaluate(e=>e.style.transform);
          await panel.locator('[data-code-expand]').click();
          assert(await page.locator('#case-code-dialog').isVisible());
          assert.equal(await page.locator('#case-code-dialog pre code').first().textContent(),snippet);
          assert.match(await page.locator('#case-code-dialog').textContent(),/ไม่ใช่.*standalone/);
          if(cid==='S01-01'){
            await page.locator('#case-code-dialog').evaluate(e=>e.dispatchEvent(new WheelEvent('wheel',{bubbles:true,cancelable:true,ctrlKey:true,deltaY:-80})));
            assert.equal(await page.locator('#diagram-stage').evaluate(e=>e.style.transform),before,'modified wheel in code viewer must not zoom the graph');
          }
          await page.locator('#case-code-dialog [data-code-original]').click();
          assert.match(await page.locator('#case-code-dialog pre code').first().textContent(),/def test_/);
          await page.locator('#case-code-dialog [data-code-example]').click();
          if(!red&&['S01-01','S03-04'].includes(cid))await page.screenshot({path:path.join(here,`qa/code-${cid}.png`)});
          await page.keyboard.press('Escape');assert.equal(await page.locator('#case-code-dialog').isVisible(),false);
          assert.equal(await page.locator('#diagram-stage').evaluate(e=>e.style.transform),before,'code viewer must not move the graph');
        }
        if(requestReview){
          assert.equal(await panel.locator('[data-detail="request"]').count(),1, `${cid} request must be visible`);
          assert.match(await panel.locator('[data-detail="request"]').textContent(), /1 HTTP request หลัก/);
          assert.equal(await panel.locator('[data-detail="request-data"]').count(),1);
          assert.equal(await panel.locator('[data-detail="request-data"] pre').count(),sid==='S02'?0:1,'do not show absent query/body as a literal null payload');
          assert.match(await panel.locator('[data-detail="request-counts"]').textContent(), /Preflight.*1/s);
          assert.equal(await panel.locator('[data-detail="request-steps"] li').count(),cid.startsWith('S01')?5:cid==='S02-03'?5:cid.startsWith('S02')?6:['S03-01','S03-04'].includes(cid)?6:2);
        }
        assert.equal(await panel.locator('[data-detail="goal"]').count(), 1, `${cid} needs a goal`);
        assert.match(await panel.locator('[data-detail="goal"]').textContent(), /ทดสอบเพื่ออะไร/);
        assert.match(await panel.locator('[data-detail="learning"]').textContent(), /ถ้า PASS เรารู้อะไร/);
        assert.match(await panel.locator('[data-detail="case-criterion"]').textContent(), /Base Choice Coverage/);
        assert.match(await panel.locator('[data-detail="recorded-result"]').textContent(), /PASS.*2026-11-09/s);
        assert.match(await panel.locator('[data-detail="recorded-result"]').textContent(), /ไม่ใช่การรันใหม่/);
        const source = await panel.locator('[data-detail="recorded-result"] a').getAttribute('href');
        assert(source.endsWith('/junit.xml'));
        assert.equal(await panel.evaluate(e => e.scrollWidth > e.clientWidth + 1), false, 'no horizontal clipping');
        if (!red && ['S01-02','S02-02','S03-04'].includes(cid)) await page.screenshot({path: path.join(here, `qa/learning-${cid}.png`)});
        if (!red && requestReview && cid==='S01-01') await page.screenshot({path:path.join(here,'qa/request-S01-01.png')});
      });
    }
  }
  if(requestReview){
    await page.locator('.jump-bar [data-focus="scope-api"]').click();
    await page.locator('#node-api-testing > header [data-pick="api-testing"]').click();
    await check('base-overview',async()=>{
      assert.equal(await panel.locator('[data-base-suite]').count(),3,'overview must explain all three bases');
      assert.equal(await panel.locator('[data-base-reason]').count(),5);
    });
  }
  await page.setViewportSize({width: 720, height: 1000}); await openSuite('S02');
  await check('mobile-panel', async () => {
    assert.equal(await panel.evaluate(e => e.scrollWidth > e.clientWidth + 1), false);
    assert.equal(await panel.locator('[data-detail="criterion"]').count(), 1);
    assert(await panel.evaluate(e => e.scrollHeight > e.clientHeight), 'long explanation must remain scrollable');
  });
  if(codeReview){
    await panel.locator('.detail-buttons > [data-pick="S02-01"]').click();await panel.locator('[data-code-open]').click();
    await check('mobile-code-viewer',async()=>{
      const bounds=await page.locator('#case-code-dialog').evaluate(e=>{const r=e.getBoundingClientRect();return{x:r.x,y:r.y,right:r.right,bottom:r.bottom,overflow:e.scrollWidth>e.clientWidth+1};});
      assert(bounds.x>=0&&bounds.y>=0&&bounds.right<=720&&bounds.bottom<=1000);assert.equal(bounds.overflow,false);
      await page.locator('#case-code-dialog .code-dialog-header button').click();assert.equal(await page.locator('#case-code-dialog').isVisible(),false);
    });
  }
  assert.deepEqual(errors, []); assert.deepEqual(external, []);
  fs.writeFileSync(path.join(here, `qa/${codeReview?'example-code':requestReview?'request-details':'learning-details'}-${red ? 'red' : 'qa'}.json`), JSON.stringify({results, errors, externalRequests: external.length, nodesVerifiedViaClicks: requestReview?19:18, source: 'local HTML only; no SUT execution'}, null, 2) + '\n');
  console.log(JSON.stringify({checks: results.length, passed: results.filter(r => r.pass).length, failures: results.filter(r => !r.pass), errors}));
  assert(results.every(r => r.pass), 'learning-detail checks failed');
} finally { await browser.close(); }
