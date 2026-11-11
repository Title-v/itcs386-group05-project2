import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
const modelPath=path.join(here,'map-model.json');
function model(){assert(fs.existsSync(modelPath),'Nested diagram model has not been built');return JSON.parse(fs.readFileSync(modelPath,'utf8'));}
test('all 17 real cases are nested inside their actual three suites',()=>{
 const m=model(),cases=m.nodes.filter(n=>n.kind==='case');
 assert.equal(cases.length,17);assert.equal(new Set(m.nodes.map(n=>n.id)).size,m.nodes.length);
 assert.deepEqual(['S01','S02','S03'].map(id=>cases.filter(n=>n.parent===id).length),[7,5,5]);
 assert(cases.every(n=>n.sources.length && n.sources[0].line>0));
});
test('normal base inputs and distinct draft/absent preconditions stay visible',()=>{
 const m=model(),n=id=>m.nodes.find(n=>n.id===id);
 assert.equal(n('S01-01').input.per_page,10);assert.equal(n('S01-01').input.search_kind,'match');
 assert.equal(n('S02-02').input.resource_state,'draft');assert.equal(n('S02-03').input.resource_state,'absent');
 assert.equal(n('S02-02').expectedStatus,404);assert.equal(n('S02-03').expectedStatus,404);
 assert.notEqual(n('S02-02').setup,n('S02-03').setup);
});
test('the deliverable is offline selectable HTML, not an image or live test runner',()=>{
 const htmlPath=path.join(here,'..','api-testing-map.html');assert(fs.existsSync(htmlPath),'HTML has not been built');
 const html=fs.readFileSync(htmlPath,'utf8');
 for(const id of ['diagram-stage','diagram-viewport','zoom-in','zoom-out','fit-view','reset-view','export-pdf','detail-panel','node-search'])assert(html.includes(`id="${id}"`),id);
 assert(!/<script[^>]+src=["']https?:/i.test(html));assert(!/\bfetch\s*\(/.test(html));
 assert(html.includes('S03-05'));assert(html.includes('data-node-id="api-testing"'));
});
test('each suite explains its actual ISP criterion, base and case count',()=>{
 const m=model(),n=id=>m.nodes.find(n=>n.id===id);
 for(const id of ['S01','S02','S03']){
  const isp=n(id).isp; assert(isp,`${id} needs an ISP explanation`);
  assert.equal(isp.code,'BCC'); assert.match(isp.name,/Base Choice Coverage/);
  assert.equal(isp.baseCase,id+'-01'); assert(isp.meaning.length>20);
  assert(isp.selection.length>=2); assert(isp.scope.length>20);
 }
 assert.equal(n('S01').isp.characteristics.length,2);
 assert.equal(n('S02').isp.characteristics.length,2);
 assert.deepEqual(n('S02').isp.characteristics.map(c=>c.type),['Functionality-based','Interface-based']);
 assert.equal(n('S03').isp.characteristics.length,2);
 assert.equal(n('S01').isp.bccCases,5); assert.equal(n('S01').isp.boundaryProbes,2);
 assert.equal(n('S02').isp.bccCases,5); assert.equal(n('S03').isp.bccCases,5);
});
test('all cases explain their own purpose, selection role and bounded learning',()=>{
 const m=model(),cases=m.nodes.filter(n=>n.kind==='case');
 for(const n of cases){
  assert(n.explanation,`${n.id} needs a per-case explanation`);
  for(const key of ['goal','role','learnIfPass','limit'])assert(n.explanation[key]?.length>15,`${n.id}.${key}`);
  assert(n.recordedResult,`${n.id} needs dated XML-backed evidence`);
  assert.equal(n.recordedResult.status,'PASS'); assert(n.recordedResult.testName.includes(n.paramId));
  assert.equal(n.recordedResult.startedBangkok,m.latestRecordedRun.started_bangkok);
  assert(n.recordedResult.file.endsWith('/junit.xml'));
 }
 assert.equal(new Set(cases.map(n=>n.explanation.goal)).size,17,'goals must be case-specific');
 assert.equal(new Set(cases.map(n=>n.explanation.learnIfPass)).size,17,'learning must be case-specific');
 assert.match(cases.find(n=>n.id==='S01-07').explanation.limit,/100/);
 assert.notEqual(cases.find(n=>n.id==='S02-02').explanation.learnIfPass,cases.find(n=>n.id==='S02-03').explanation.learnIfPass);
});
test('base choices give concrete values and a reason for every characteristic',()=>{
 const m=model();
 for(const suite of m.nodes.filter(n=>n.kind==='suite')){
  for(const c of suite.isp.characteristics){
   const choice=suite.isp.baseChoices?.[c.id]; assert(choice,`${suite.id}/${c.id} needs a base value and reason`);
   assert.equal(choice.block,c.baseBlock); assert(choice.value.length>3); assert(choice.reason.length>20);
  }
 }
});
test('requests are bound to recorded traffic and distinguish HTTP calls from products',()=>{
 const m=model(),n=id=>m.nodes.find(n=>n.id===id),cases=m.nodes.filter(n=>n.kind==='case');
 for(const c of cases){
  assert(c.request,`${c.id} needs the actual HTTP request`);
  assert.equal(c.request.count,1); assert.equal(c.request.status,c.expectedStatus);
  assert.equal(c.traffic.counts.underTest,1);
  assert.equal(c.traffic.total,Object.values(c.traffic.counts).reduce((a,b)=>a+b,0));
  assert.equal(c.traffic.total,c.traffic.steps.length);
  assert(c.traffic.source.endsWith('/console.txt'));
  assert(c.traffic.steps.every(s=>s.line>0 && s.method && s.path));
  assert(!Object.keys(c.request.query||{}).includes('expected_status'));
 }
 assert.deepEqual(n('S01-01').traffic.counts,{setup:1,underTest:1,verification:0,cleanup:3});
 assert.equal(n('S01-01').traffic.total,5);
 assert.equal(n('S01-01').request.query.per_page,10);
 assert(n('S01-01').request.query.search.startsWith('G05-'));
 assert.equal(n('S01-01').request.response.count,1);
 assert.equal(n('S01-01').request.body,null);
 assert.equal(n('S01-04').request.query.search,undefined);
 assert.deepEqual(n('S02-03').traffic.counts,{setup:4,underTest:1,verification:0,cleanup:0});
 assert.deepEqual(n('S03-01').traffic.counts,{setup:0,underTest:1,verification:2,cleanup:3});
 assert.deepEqual(n('S03-02').traffic.counts,{setup:0,underTest:1,verification:1,cleanup:0});
 assert.equal(n('S03-01').request.body.type,'simple'); assert.equal(n('S03-01').request.body.regular_price,'100.00');
 assert.equal(n('S03-02').request.authMode,'missing');
 assert.equal(n('S03-03').request.authMode,'wrong');
 assert.equal(n('S02-01').request.query,null);
 assert.deepEqual(n('S02-04').request.query,{context:'view'}); assert.equal(n('S02-04').request.status,200);
 assert.deepEqual(n('S02-05').request.query,{context:'not-a-context'}); assert.equal(n('S02-05').request.status,400);
 assert.deepEqual(n('S02-04').traffic.counts,{setup:2,underTest:1,verification:0,cleanup:3});
 assert.equal(m.recordedTraffic.sharedPreflight.length,1);
 assert.equal(m.recordedTraffic.total,83);
 assert.equal(cases.reduce((sum,c)=>sum+c.traffic.total,0),82);
});
test('every displayed case name states the action and its distinguishing condition',()=>{
 const expected={
  'S01-01':'ค้นหาสินค้าด้วยชื่อที่ตรงกัน',
  'S01-02':'ค้นหาสินค้าโดยส่ง per_page=0',
  'S01-03':'ค้นหาสินค้าโดยส่ง per_page=101',
  'S01-04':'อ่านรายการสินค้าโดยไม่ระบุคำค้น',
  'S01-05':'ค้นหาด้วยชื่อที่ไม่ตรงกับสินค้า',
  'S01-06':'ค้นหาสินค้าโดยขอสูงสุด 1 รายการ',
  'S01-07':'ค้นหาสินค้าโดยขอสูงสุด 100 รายการ',
  'S02-01':'อ่านสินค้าที่เผยแพร่แล้วด้วย ID',
  'S02-02':'ขออ่าน draft ด้วย ID — ต้องไม่เปิดเผย',
  'S02-03':'ขอข้อมูลสินค้าที่ลบแล้วด้วย ID',
  'S02-04':'อ่านสินค้าโดยส่ง context=view',
  'S02-05':'อ่านสินค้าโดยส่ง context ที่ไม่ถูกต้อง',
  'S03-01':'สร้างและเผยแพร่สินค้าด้วยสิทธิ์ถูกต้อง',
  'S03-02':'ขอสร้างสินค้าโดยไม่ส่ง credentials',
  'S03-03':'ขอสร้างสินค้าโดยใช้ password ผิด',
  'S03-04':'สร้างสินค้าเป็น draft ไม่เผยแพร่',
  'S03-05':'ขอสร้างสินค้าด้วย status ที่ไม่ถูกต้อง'
 };
 const m=model();
 for(const [id,title]of Object.entries(expected))assert.equal(m.nodes.find(n=>n.id===id).title,title,id);
 assert.match(m.nodes.find(n=>n.id==='S01').title,/ตามชื่อ/);
});
test('all 17 cases have readable bound examples and their unchanged original source',()=>{
 const cases=model().nodes.filter(n=>n.kind==='case');
 for(const n of cases){
  assert(n.exampleCode,`${n.id} needs example code`);
  assert.match(n.exampleCode.code,new RegExp(`def example_${n.id.toLowerCase().replaceAll('-','_')}\\(api, products\\):`));
  assert(n.exampleCode.code.includes('assert'));
  assert.equal(n.exampleCode.originalFunction,n.sources[1].excerpt);
  assert.equal(n.exampleCode.originalParameter,n.sources[0].excerpt);
  assert.equal(n.exampleCode.standalone,false);
  assert.equal(n.exampleCode.executedInBrowser,false);
 }
 const by=id=>cases.find(n=>n.id===id).exampleCode.code;
 assert(by('S01-02').includes("assert_error(response, 400, 'rest_invalid_param')"));
 assert(!by('S01-02').includes('assert_store_product'));
 assert(!by('S01-04').includes("query['search']"));
 assert(by('S01-05').includes('uuid4'));
 assert(by('S02-03').includes('delete_owned'));
 assert(by('S03-04').includes('assert_error(shopper_view, 404)'));
 assert(by('S03-03').includes("auth_mode = 'wrong'") || by('S03-03').includes("products.submit(payload, 'wrong')"));
});
