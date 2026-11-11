(() => {
  'use strict';
  const model=JSON.parse(document.getElementById('map-data').textContent);
  const nodes=new Map(model.nodes.map(n=>[n.id,n]));
  const details=document.getElementById('node-details'),note=document.getElementById('node-note');
  const status=document.getElementById('note-status'),search=document.getElementById('node-search');
  const NS='itcs386-api-map-notes-v1';let selected='scope-api',notes={};
  const VIEW_NS='itcs386-api-map-view-v1',panel=document.getElementById('detail-panel');
  let readyToSaveView=false,printSelection=null,printView=null;
  try{notes=JSON.parse(localStorage.getItem(NS)||'{}');}catch{}
  const disclosureKey=d=>d.dataset.detail||d.querySelector(':scope > summary')?.textContent;
  const viewSnapshot=()=>({version:1,selected,view:window.diagramControls.state(),panel:{scrollTop:panel.scrollTop,openDetails:[...details.querySelectorAll('details[open]')].map(disclosureKey)}});
  function saveView(){
    if(!readyToSaveView || printSelection!==null)return;
    try{localStorage.setItem(VIEW_NS,JSON.stringify(viewSnapshot()));}catch{}
  }
  function restorePanel(saved){
    const open=new Set(Array.isArray(saved?.openDetails)?saved.openDetails:[]);
    for(const d of details.querySelectorAll('details'))d.open=open.has(disclosureKey(d));
    if(Number.isFinite(saved?.scrollTop)&&saved.scrollTop>=0)panel.scrollTop=saved.scrollTop;
  }
  const el=(tag,text,cls)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;};
  const button=(id,label,focus=false)=>{const b=el('button',label||nodes.get(id)?.title||id);b.type='button';b.dataset[focus?'focus':'pick']=id;return b;};
  const list=(parent,title,items)=>{if(!items?.length)return;parent.append(el('h3',title));const ul=el('ul',undefined,'detail-list');for(const item of items)ul.append(el('li',typeof item==='string'?item:JSON.stringify(item)));parent.append(ul);};
  const detailSection=(key,title,text,cls='')=>{const s=el('section',undefined,'learning-section '+cls);s.dataset.detail=key;s.append(el('h3',title));if(text)s.append(el('p',text));return s;};
  const codeBlock=text=>{const pre=el('pre',undefined,'case-code');pre.append(el('code',text));return pre;};
  const codeContext='ตัวอย่างสำหรับอ่านที่ derive จาก source และแทนค่าของ case นี้ ไม่ใช่สคริปต์ standalone: ต้องใช้ api/products fixtures ของโปรเจกต์ ไม่ได้รันใน Browser หรือเพิ่ม test case ใหม่';
  const cleanupContext='Cleanup ไม่ได้อยู่ใน snippet นี้: เมื่อรันผ่าน pytest ของโปรเจกต์ products fixture จะ cleanup ใน finally ของ conftest.py ห้ามแยก POST ออกไปรันโดยข้าม fixtures/cleanup';
  function originalCode(n){return '# Selected pytest parameter row (original)\n'+n.exampleCode.originalParameter+'\n\n# Shared test function (original)\n'+n.exampleCode.originalFunction;}
  function openCode(n){
    let dialog=document.getElementById('case-code-dialog');
    if(!dialog){dialog=el('dialog',undefined,'case-code-dialog');dialog.id='case-code-dialog';dialog.setAttribute('aria-labelledby','case-code-heading');document.body.append(dialog);}
    dialog.replaceChildren();const header=el('header',undefined,'code-dialog-header'),title=el('h2',n.id+' · '+n.title);title.id='case-code-heading';
    const close=el('button','ปิด');close.type='button';close.addEventListener('click',()=>dialog.close());header.append(title,close);
    const tabs=el('div',undefined,'code-actions'),example=el('button','Example ของ case นี้'),original=el('button','โค้ดต้นฉบับ');
    example.type=original.type='button';example.dataset.codeExample='';original.dataset.codeOriginal='';tabs.append(example,original);
    const pre=codeBlock(n.exampleCode.code);
    const show=mode=>{pre.firstChild.textContent=mode==='example'?n.exampleCode.code:originalCode(n);example.setAttribute('aria-pressed',String(mode==='example'));original.setAttribute('aria-pressed',String(mode==='original'));};
    example.addEventListener('click',()=>show('example'));original.addEventListener('click',()=>show('original'));
    dialog.append(header,el('p',codeContext,'code-disclaimer'),tabs,pre,el('p',cleanupContext,'code-disclaimer'),el('p',n.exampleCode.file+':'+n.exampleCode.line,'source-ref'));
    show('example');dialog.showModal();
  }
  function exampleSection(n){
    const section=detailSection('example-code','Example code · Python');
    section.append(el('p',codeContext,'muted'),codeBlock(n.exampleCode.code));
    const actions=el('div',undefined,'code-actions'),expand=el('button','ขยายโค้ด / ดูต้นฉบับ');expand.type='button';expand.dataset.codeExpand='';expand.addEventListener('click',()=>openCode(n));actions.append(expand);
    section.append(actions,el('p',cleanupContext,'muted'));
    const helpers=el('details');helpers.append(el('summary','fixtures และ helper assertions คืออะไร?'));
    list(helpers,'ใช้ของโปรเจกต์เดิม',[
      'api: HTTP client แยก Store (public) และ Admin (credentials) ให้ ไม่ใช่ JavaScript ใน Browser',
      'products: เตรียมข้อมูลแยกแต่ละ case, ตรวจ ownership ก่อนลบ และ cleanup ใน finally ของ pytest fixture',
      'assert_error: ตรวจ status และ JSON code/message/data.status ไม่ใช่ดูแค่ HTTP code',
      'assert_store_product: ตรวจ ID/name และราคา THB โดย 10000 minor units = 100.00 THB',
      'is_owned_product: ตรวจ ID/name และ run marker ให้ตรงก่อนถือว่าเป็นข้อมูลของ test นี้'
    ]);section.append(helpers);return section;
  }
  function baseCard(n){
    const isp=n.isp,base=detailSection('base-choice',n.id+' · Base ที่เลือก',isp.base,'base-card');base.dataset.baseSuite=n.id;
    base.append(el('h4','ทำไมเลือก Base นี้?'));
    for(const [cid,choice] of Object.entries(isp.baseChoices)){
      const reason=el('div',undefined,'base-reason');reason.dataset.baseReason=cid;
      reason.append(el('strong',cid+'-'+choice.block+' · '+choice.value),el('p',choice.reason));base.append(reason);
    }
    base.append(el('p',isp.fixedSetup,'muted'),button(isp.baseCase,'ดู '+isp.baseCase+' · base case'));return base;
  }
  function explainSuite(n){
    const isp=n.isp;
    details.append(baseCard(n));
    const criterion=detailSection('criterion','ISP coverage criterion',undefined,'criterion-card');
    criterion.append(el('strong',isp.name),el('p',isp.meaning));details.append(criterion);
    const selection=detailSection('case-selection','เลือก Test cases อย่างไร?');
    const steps=el('ol',undefined,'detail-list');for(const step of isp.selection)steps.append(el('li',step));selection.append(steps);
    const count=el('p',isp.count,'criterion-count');count.dataset.detail='criterion-count';selection.append(count);details.append(selection);
    const characteristics=el('section',undefined,'learning-section');characteristics.dataset.detail='characteristics';
    const disclosure=el('details');disclosure.append(el('summary','ดู Characteristics และ Blocks'));
    disclosure.append(el('p','Characteristic type บอกว่าแบ่ง input จากอะไร ส่วน coverage criterion บอกว่าเลือก combinations ใดมาทดสอบ','muted'));
    for(const c of isp.characteristics){
      const block=el('div',undefined,'characteristic-card');block.append(el('h4',c.id+' · '+c.name),el('p',c.type,'characteristic-type'));
      const ul=el('ul',undefined,'detail-list');for(const b of c.blocks)ul.append(el('li',b.id+(b.id===c.baseBlock?' (base)':'')+' · '+b.label+' — ใช้ '+b.representative));
      block.append(ul);disclosure.append(block);
    }
    characteristics.append(disclosure);details.append(characteristics);
    details.append(detailSection('scope-limit','Scope · ยืนยันได้แค่ไหน?',isp.scope,'learning-limit'));
  }
  function explainRequests(n){
    const r=n.request,t=n.traffic,request=detailSection('request','ส่ง Request อะไร?',undefined,'request-card');
    request.append(el('strong','1 HTTP request หลัก'),el('code',r.method+' '+r.path,'request-route'));
    request.append(el('p','Path ต่อจาก /shop/wp-json · '+(r.authMode==='public/no-auth'?'Public / ไม่ส่ง credentials':r.authMode==='valid'?'Basic auth ถูกต้อง':r.authMode==='missing'?'ไม่ส่ง credentials':'Basic auth ใช้ password ผิด'),'muted'));
    request.append(el('p',r.quantity));
    if(r.query)request.append(el('p',Object.entries(r.query).map(([k,v])=>k+'='+v).join(' · '),'request-values'));
    if(r.body)request.append(el('p','type='+r.body.type+' · status='+r.body.status+' · regular_price='+r.body.regular_price,'request-values'));
    const response=r.response;
    const itemCount=Number.isInteger(response.count)?response.count:Number.isInteger(response.id)?1:null;
    request.append(el('p','Response รอบบันทึก: HTTP '+r.status+(itemCount===null?' · JSON error':' · '+itemCount+' สินค้า'),'recorded-response'));
    const data=el('details');data.dataset.detail='request-data';data.append(el('summary','ดู Query / Body ที่ส่งจริง'));
    data.append(el('p',r.query?'Query parameters':'Query: ไม่ส่ง'));if(r.query)data.append(el('pre',JSON.stringify(r.query,null,2),'source-excerpt'));
    data.append(el('p',r.body?'JSON body':'Body: ไม่มี'));if(r.body)data.append(el('pre',JSON.stringify(r.body,null,2),'source-excerpt'));
    data.append(el('p','ชื่อ/SKU/ID เป็นค่าจากรอบบันทึกและเปลี่ยนใหม่แต่ละ case; fixture ถูก cleanup แล้ว ไม่ใช่ค่าที่ต้องนำไปใช้ซ้ำ ไม่มีรหัสผ่านจริงในหน้านี้','muted'));request.append(data);details.append(request);
    const counts=detailSection('request-counts','ถ้านับ HTTP requests ทั้ง case ล่ะ?');
    counts.append(el('strong','รวม '+t.total+' requests ในรอบบันทึก'));
    counts.append(el('p','Setup '+t.counts.setup+' + ทดสอบหลัก '+t.counts.underTest+' + ตรวจยืนยัน '+t.counts.verification+' + Cleanup '+t.counts.cleanup));
    counts.append(el('p','Preflight อีก 1 request ต่อ pytest run ใช้ร่วมกัน ไม่ได้นับซ้ำทุก case; ถ้ารัน case เดียวตาม flow นี้จะรวม '+(t.total+1)+' requests','muted'));
    const sequence=el('details');sequence.dataset.detail='request-steps';sequence.append(el('summary','ดูลำดับ requests ทั้ง '+t.total+' ครั้ง'));
    const steps=el('ol',undefined,'request-steps');const phases={setup:'Setup · เตรียมสถานการณ์',underTest:'Request หลักที่ทดสอบ',verification:'ตรวจยืนยันผล',cleanup:'Cleanup · ตรวจ/ลบ/ยืนยัน'};
    for(const step of t.steps){
      const li=el('li');li.append(el('strong',phases[step.phase]),el('code',step.method+' '+step.path,'request-route'),el('span',' → HTTP '+step.status));
      if(step.query)li.append(el('pre',JSON.stringify(step.query,null,2),'source-excerpt'));
      if(step.input){const body=el('details');body.append(el('summary','JSON body'),el('pre',JSON.stringify(step.input,null,2),'source-excerpt'));li.append(body);}
      steps.append(li);
    }
    sequence.append(steps,el('p','Preflight ที่ใช้ร่วมกัน: GET /wc/v3/products?per_page=1 ด้วย valid auth ก่อนเริ่ม fixtures','muted'));counts.append(sequence);
    counts.append(el('p','นับจาก log วันที่ '+n.recordedResult.startedBangkok.slice(0,10)+' Bangkok; หาก setup/error/cleanup เปลี่ยน จำนวนอาจต่างออกไป ไม่ใช่การรันใหม่','muted'));
    const link=el('a','เปิด console log ที่ใช้นับ','source-ref');link.href='../'+t.source.split('/').map(encodeURIComponent).join('/');link.target='_blank';link.rel='noopener';counts.append(link);details.append(counts);
  }
  function explainCase(n){
    const isp=nodes.get(n.parent).isp,ex=n.explanation;
    explainRequests(n);
    details.append(detailSection('goal','ทดสอบเพื่ออะไร?',ex.goal,'goal-card'));
    details.append(exampleSection(n));
    details.append(detailSection('learning','ถ้า PASS เรารู้อะไร?',ex.learnIfPass));
    const criterion=detailSection('case-criterion','Case นี้มาจาก ISP อย่างไร?');
    criterion.append(el('strong',isp.name),el('p','Base ของ Suite: '+isp.base),el('p',ex.role),button(n.parent,'ดู Base และเหตุผลของ '+n.parent));details.append(criterion);
    details.append(detailSection('case-limit','สิ่งที่ยังสรุปไม่ได้',ex.limit,'learning-limit'));
    const r=n.recordedResult,record=detailSection('recorded-result','ผลที่บันทึกจากการรัน');record.dataset.result=r.status;
    record.append(el('strong',r.status+' · '+r.startedBangkok.slice(0,10)+' '+r.startedBangkok.slice(11,19)+' Bangkok'));
    record.append(el('p','อ่านจาก JUnit XML ของรอบนี้ ไม่ใช่การรันใหม่เมื่อคลิกกราฟ','muted'));
    const link=el('a','เปิด JUnit XML','source-ref');link.href='../'+r.file.split('/').map(encodeURIComponent).join('/');link.target='_blank';link.rel='noopener';record.append(link);details.append(record);
    if(n.expectedStatus>=400)details.append(el('p','HTTP '+n.expectedStatus+' เป็น expected result ของ case นี้ ไม่ใช่ test FAIL; ต้องตรงทั้ง status และ assertions อื่นจึงจะ PASS','negative-result-note'));
  }
  function select(id,focus=false,preserveView=false){
    if(!nodes.has(id))return;selected=id;const n=nodes.get(id);
    document.querySelectorAll('.is-selected').forEach(e=>e.classList.remove('is-selected'));
    const box=document.getElementById('node-'+id);box?.classList.add('is-selected');
    details.replaceChildren();const ref=el('div',undefined,'detail-ref');ref.append(el('span',n.id),el('span',n.kind==='concept'?'Conceptual · ไม่ inspect ภายใน':'Source-backed',n.kind==='concept'?'detail-tag concept':'detail-tag'));details.append(ref,el('h2',n.title),el('p',n.what));
    if(n.exampleCode){const actions=el('div',undefined,'code-actions'),open=el('button','ดู Example code');open.type='button';open.dataset.codeOpen='';open.addEventListener('click',()=>openCode(n));actions.append(open);details.append(actions);}
    if(n.isp)explainSuite(n);
    else if(n.explanation)explainCase(n);
    else if(n.why){details.append(el('h3','ทำไมต้องมีส่วนนี้?'),el('p',n.why));}
    if(id==='api-testing'){
      details.append(el('h3','Base choices ของทั้ง 3 Suites'),el('p','แต่ละ Suite มี base ของตัวเอง แล้วเปลี่ยนทีละ characteristic; ไม่ได้ใช้ base เดียวร่วมกันทุก operation'));
      for(const child of n.children){const suite=nodes.get(child);if(suite.isp)details.append(baseCard(suite));}
    }
    if(n.setup){details.append(el('h3','Arrange · เตรียมสถานการณ์'),el('p',n.setup));}
    if(n.input){const params=el('details');params.append(el('summary','ดู test parameters และ ISP blocks (ไม่ใช่ HTTP payload)'),el('pre',JSON.stringify(n.input,null,2),'source-excerpt'),el('p','ISP: '+n.blocks));details.append(params);}
    if(!n.isp){list(details,'รับอะไรเข้าไป?',n.inputs);list(details,n.kind==='case'?'Expected result · ตรวจอะไรบ้าง?':'คาดหวัง / ส่งอะไรออกมา?',n.outputs);}
    if(n.parent){const crumb=el('div',undefined,'detail-buttons');crumb.append(button(n.parent,'↑ '+nodes.get(n.parent).title,true));details.append(crumb);}
    if(n.children.length){details.append(el('h3',n.kind==='suite'?'Test cases ใน Suite นี้':'ส่วนย่อยที่อยู่ข้างใน'));const c=el('div',undefined,'detail-buttons');if(n.kind==='suite')c.dataset.detail='suite-cases';for(const child of n.children)c.append(button(child,child+' · '+nodes.get(child).title));details.append(c);}
    const connected=model.relations.filter(r=>r.source===id||r.target===id);
    if(connected.length){details.append(el('h3','Connections · ทำงานกับอะไร?'));for(const r of connected){const other=r.source===id?r.target:r.source;const p=el('p');p.append(el('span',r.source===id?'→ ':'← '),button(other,nodes.get(other).title),el('span',' — '+r.label));details.append(p);}}
    if(n.sources.length){details.append(el('h3','หลักฐานจากไฟล์จริง'));for(const s of n.sources){const a=el('a',s.file+':'+s.line,'source-ref');a.href='../'+s.file.split('/').map(encodeURIComponent).join('/')+'#L'+s.line;a.target='_blank';a.rel='noopener';details.append(a);}
      const disclosure=el('details');disclosure.append(el('summary','ดู source excerpt (ไม่จำเป็นต้องอ่านเพื่อเข้าใจภาพรวม)'),el('pre',n.sources[0].excerpt,'source-excerpt'));details.append(disclosure);}
    if(n.graphRefs.length){const p=el('p','Graphify reference: '+n.graphRefs.join(', '),'muted');details.append(p);}
    note.value=notes[id]?.text||'';status.textContent='โน้ตผูกกับ '+id+' · ยังไม่ส่งหรือเปลี่ยนโค้ด';
    if(!preserveView && (focus || (box && !box.getClientRects().length))){let target=id;while(target){const candidate=document.getElementById('node-'+target);if(candidate&&candidate.getClientRects().length)break;target=nodes.get(target)?.parent;}if(target)window.diagramControls.focus(target);const revealed=document.getElementById('node-'+id);if(target!==id&&revealed?.getClientRects().length)window.diagramControls.focus(id);}
    if(history.replaceState)try{history.replaceState(null,'','#'+encodeURIComponent(id));}catch{}
    document.getElementById('detail-panel').scrollTop=0;
    drawConnections();
    saveView();
  }
  document.addEventListener('click',e=>{const focus=e.target.closest('[data-focus]'),pick=e.target.closest('[data-pick]');if(focus){select(focus.dataset.focus,true);return;}if(pick)select(pick.dataset.pick);});
  search.addEventListener('input',()=>{const q=search.value.trim().toLowerCase(),out=document.getElementById('search-results');out.replaceChildren();if(!q)return;for(const n of model.nodes.filter(n=>(n.id+' '+n.title+' '+n.what).toLowerCase().includes(q)).slice(0,12))out.append(button(n.id,n.id+' · '+n.title,true));});
  document.getElementById('save-note').addEventListener('click',()=>{notes[selected]={id:selected,title:nodes.get(selected).title,text:note.value,updatedAt:new Date().toISOString()};try{localStorage.setItem(NS,JSON.stringify(notes));status.textContent='บันทึกใน browser นี้แล้ว · ใช้ Export notes เพื่อส่งต่อ';}catch{status.textContent='browser ไม่ให้เก็บถาวร · โน้ตยัง export ได้ใน session นี้';}});
  document.getElementById('copy-ref').addEventListener('click',async()=>{const text=selected+' — '+nodes.get(selected).title;try{await navigator.clipboard.writeText(text);status.textContent='คัดลอก '+selected+' แล้ว';}catch{status.textContent='คัดลอกด้วยตัวเองได้: '+text;}});
  document.getElementById('export-notes').addEventListener('click',()=>{const blob=new Blob([JSON.stringify({artifact:'API testing nested map',graphSha256:model.graph.sha256,exportedAt:new Date().toISOString(),notes:Object.values(notes)},null,2)],{type:'application/json'});const url=URL.createObjectURL(blob),a=el('a');a.href=url;a.download='api-testing-map-notes.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status.textContent='Export โน้ตแล้ว · ไม่มีการส่งเข้า server';});
  const svgNS='http://www.w3.org/2000/svg',paths=document.getElementById('connection-paths');
  function drawConnections(){
    paths.replaceChildren();
    // Parent-level routing keeps connections out of the nested case text. Selecting a case
    // highlights its suite; exact case/helper connections remain in the source-backed sidebar.
    const suite=nodes.get(selected)?.kind==='case'?nodes.get(selected).parent:selected;
    const all=selected==='scope-api';
    const specs=[
      {ids:['scope-api','api-testing','pytest','api-runner'],d:'M577 940 H695',x:648,y:917,label:'runs'},
      {ids:['scope-api','S01','S02','S03','api-testing','store-api','store-client'],d:'M2050 725 H2175',x:2112,y:698,label:'GET'},
      {ids:['scope-api','S03','api-testing','admin-api','admin-client'],d:'M2050 1015 H2175',x:2112,y:990,label:'POST'},
      {ids:['scope-api','fixtures','products-fixture','cleanup-ownership','unknown-post','admin-api'],d:'M577 1590 H655 V2125 H2105 V1070 H2175',x:1400,y:2116,label:'fixture / cleanup · Admin API'},
      {ids:['api-runner','evidence','evidence-console','evidence-junit','evidence-manifest'],d:'M577 680 H655 V397 H2105 V1545 H2140',x:1370,y:390,label:'runner writes evidence'},
    ];
    const helperTargets={'store-client':'store-api','admin-client':'admin-api','products-fixture':'admin-api','cleanup-ownership':'admin-api'};
    let visibleSpecs=specs.filter(s=>all?s.ids.includes('scope-api'):s.ids.includes(suite)||s.ids.includes(selected));
    if(helperTargets[selected]){
      const stage=document.getElementById('diagram-stage'),origin=stage.getBoundingClientRect(),scale=window.diagramControls.state().zoom;
      const logical=id=>{const r=document.getElementById('node-'+id).getBoundingClientRect();return{x:(r.left-origin.left)/scale,y:(r.top-origin.top)/scale,w:r.width/scale,h:r.height/scale};};
      const a=logical(selected),b=logical(helperTargets[selected]);
      if(a.w&&b.w){
        let start=`M${a.x+a.w} ${a.y+a.h/2} H655`;
        if(selected==='store-client'){const parent=logical('clients');start=`M${a.x+a.w/2} ${a.y+a.h} V${parent.y+parent.h+7} H655`;}
        const endY=b.y+b.h/2;
        visibleSpecs=[{d:`${start} V2125 H2105 V${endY} H${b.x}`,x:1400,y:2116,label:selected==='store-client'?'public Store requests · no group credentials':'Admin requests · exact scoped test data'}];
      }
    }
    for(const s of visibleSpecs){const p=document.createElementNS(svgNS,'path');p.setAttribute('d',s.d);p.setAttribute('class','connection-line'+(s.inferred?' inferred':''));paths.append(p);const t=document.createElementNS(svgNS,'text');t.setAttribute('x',s.x);t.setAttribute('y',s.y);t.setAttribute('text-anchor','middle');t.setAttribute('class','edge-label');t.textContent=s.label;paths.append(t);}
  }
  window.addEventListener('beforeprint',()=>{printView=viewSnapshot();printSelection=selected;select('scope-api',false,true);});
  window.addEventListener('afterprint',()=>{if(printView){window.diagramControls.restore(printView.view);select(printView.selected,false,true);restorePanel(printView.panel);}printSelection=null;printView=null;saveView();});
  window.addEventListener('diagram-view',e=>{document.getElementById('lod-label').textContent=e.detail.zoom<.52?'ภาพรวม':e.detail.zoom<.86?'Modules':'Cases / detail';saveView();});
  panel.addEventListener('scroll',saveView,{passive:true});
  details.addEventListener('toggle',saveView,true);
  window.addEventListener('pagehide',saveView);
  document.addEventListener('visibilitychange',()=>{if(document.hidden)saveView();});
  window.addEventListener('hashchange',()=>{const id=decodeURIComponent(location.hash.slice(1));if(nodes.has(id)&&id!==selected)select(id,true);});
  window.apiMap={model,select,notes:()=>({...notes})};
  const initial=decodeURIComponent(location.hash.slice(1));let savedView=null;
  try{savedView=JSON.parse(localStorage.getItem(VIEW_NS)||'null');}catch{}
  const canRestore=savedView?.version===1&&nodes.has(savedView.selected)&&(!initial||initial===savedView.selected)&&window.diagramControls.restore(savedView.view);
  if(canRestore){select(savedView.selected,false,true);restorePanel(savedView.panel);}
  else select(nodes.has(initial)?initial:'scope-api',Boolean(initial&&nodes.has(initial)));
  readyToSaveView=true;saveView();
})();
