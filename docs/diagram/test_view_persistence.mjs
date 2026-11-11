import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE ?? 'playwright');
const here=path.dirname(fileURLToPath(import.meta.url)),url=pathToFileURL(path.resolve(here,'../api-testing-map.html')).href;
const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
const context=await browser.newContext({viewport:{width:1440,height:1000}});
let page=await context.newPage();const results=[],errors=[],key='itcs386-api-map-view-v1';
const watch=p=>p.on('pageerror',e=>errors.push(e.message));watch(page);
const read=()=>page.evaluate(()=>{const s=document.querySelector('#diagram-stage'),v=document.querySelector('#diagram-viewport'),m=new DOMMatrix(getComputedStyle(s).transform);return{zoom:m.a,x:m.e,y:m.f,anchorX:(v.clientWidth/2-m.e)/m.a,anchorY:(v.clientHeight/2-m.f)/m.a,mode:s.dataset.viewMode,selected:document.querySelector('#node-details .detail-ref span').textContent,scroll:document.querySelector('#detail-panel').scrollTop,open:[...document.querySelectorAll('#node-details details[open]')].map(e=>e.querySelector('summary').textContent)}});
const near=(a,b,label)=>assert(Math.abs(a-b)<0.05,`${label}: ${a} != ${b}`);
const check=async(name,fn)=>{try{await fn();results.push({name,pass:true});}catch(e){results.push({name,pass:false,error:e.message});}};
try{
 await page.goto(url+'#S01-01');
 for(const percent of [90,80,100])await check(`${percent}% pan / selected case / panel scroll and disclosures survive Refresh`,async()=>{
  await page.goto(url+'#S01-01');await page.locator('#reset-view').click();
  for(let p=100;p>percent;p-=10)await page.locator('#zoom-out').click();
  await page.mouse.move(80,150);await page.keyboard.down('Meta');await page.mouse.down();await page.mouse.move(50,210,{steps:4});await page.mouse.up();await page.keyboard.up('Meta');
  const disclosure=page.locator('[data-detail="request-data"]');if(await disclosure.getAttribute('open')===null)await disclosure.locator('summary').click();
  await page.locator('#detail-panel').evaluate(e=>{e.scrollTop=430;});await page.waitForTimeout(80);
  const before=await read();assert(Math.abs(before.zoom-percent/100)<0.001);
  await page.reload();const after=await read();near(after.zoom,before.zoom,'zoom');near(after.x,before.x,'pan x');near(after.y,before.y,'pan y');
  assert.equal(after.selected,before.selected);near(after.scroll,before.scroll,'panel scroll');assert.deepEqual(after.open,before.open);
 });
 await check('Fit remains Fit after Refresh',async()=>{
  await page.locator('#fit-view').click();const before=await read();await page.reload();const after=await read();
  assert.equal(after.mode,'fit');near(after.zoom,before.zoom,'Fit zoom');near(after.x,before.x,'Fit x');
 });
 await check('PDF export does not replace the saved review position',async()=>{
  await page.locator('#reset-view').click();await page.locator('#zoom-out').click();
  await page.locator('[data-detail="request-data"] summary').click();await page.locator('#detail-panel').evaluate(e=>{e.scrollTop=380;});await page.waitForTimeout(80);
  const before=await read();await page.pdf({preferCSSPageSize:true});await page.reload();const after=await read();
  assert.equal(after.selected,before.selected);near(after.zoom,before.zoom,'post-print zoom');near(after.x,before.x,'post-print pan x');near(after.y,before.y,'post-print pan y');near(after.scroll,before.scroll,'post-print panel scroll');
 });
 await check('a new window size retains manual zoom and center anchor',async()=>{
  await page.locator('#reset-view').click();await page.locator('#zoom-out').click();
  await page.mouse.move(600,125);await page.keyboard.down('Meta');await page.mouse.down();await page.mouse.move(300,125,{steps:4});await page.mouse.up();await page.keyboard.up('Meta');
  const before=await read();await page.close();
  page=await context.newPage();watch(page);await page.setViewportSize({width:1800,height:1100});await page.goto(url+'#S01-01');const after=await read();
  near(after.zoom,before.zoom,'manual zoom');near(after.anchorX,before.anchorX,'center x');near(after.anchorY,before.anchorY,'center y');
 });
 await check('explicit different node deep link takes priority over saved selection',async()=>{
  await page.goto(url+'#S03');const current=await read();assert.equal(current.selected,'S03');
 });
 await check('corrupt saved state is ignored without breaking controls',async()=>{
  await page.evaluate(k=>localStorage.setItem(k,'broken JSON'),key);await page.reload();await page.locator('#reset-view').click();near((await read()).zoom,1,'Reset after corrupt state');
 });
 await check('invalid numeric state cannot produce NaN transforms',async()=>{
  await page.evaluate(k=>localStorage.setItem(k,JSON.stringify({version:1,selected:'S03',view:{zoom:'NaN',pan:{x:0,y:0},mode:'manual'}})),key);await page.reload();const current=await read();assert(Number.isFinite(current.zoom)&&Number.isFinite(current.x));
 });
 await check('saving the view does not alter saved annotations',async()=>{
  const notesKey='itcs386-api-map-notes-v1',notes=JSON.stringify({'S01-01':{id:'S01-01',text:'QA keep existing notes'}});
  await page.evaluate(({notesKey,notes})=>localStorage.setItem(notesKey,notes),{notesKey,notes});await page.locator('#zoom-out').click();await page.reload();
  assert.equal(await page.evaluate(k=>localStorage.getItem(k),notesKey),notes);
 });
 await check('storage-denied browser still loads and navigates',async()=>{
  const isolated=await browser.newContext();const p=await isolated.newPage();watch(p);
  try{await p.addInitScript(()=>{Storage.prototype.getItem=function(){throw new DOMException('denied','SecurityError');};Storage.prototype.setItem=function(){throw new DOMException('denied','SecurityError');};});await p.goto(url);await p.locator('#reset-view').click();assert.equal(await p.locator('#zoom-value').textContent(),'100%');}
  finally{await isolated.close();}
 });
 assert.deepEqual(errors,[]);
 const report={results,errors,storageKey:key,source:'isolated local browser; no API tests or classroom requests'};
 fs.writeFileSync(path.join(here,`qa/view-persistence-${process.argv.includes('--red')?'red':'qa'}.json`),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report));assert(results.every(r=>r.pass),'view persistence checks failed');
}finally{await browser.close();}
