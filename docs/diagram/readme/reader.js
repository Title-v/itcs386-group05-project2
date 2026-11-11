(function(){
  'use strict';
  const docKey='itcs386-phase2-api-readme-scratch-v1';
  const viewer=document.querySelector('.viewer'),frame=document.querySelector('.scale-frame'),stage=document.querySelector('.stage'),paper=document.querySelector('#paper');
  const gutter=document.querySelector('.line-gutter'),hint=document.querySelector('.line-hint');
  const zoomOut=document.querySelector('[data-action="zoom-out"]'),zoomIn=document.querySelector('[data-action="zoom-in"]'),zoomReset=document.querySelector('[data-action="zoom-reset"]'),zoomText=document.querySelector('.zoom-readout'),themeButton=document.querySelector('.theme-button');
  let saved={};try{saved=JSON.parse(localStorage.getItem(docKey)||'{}')||{};}catch(_){saved={};}
  let zoom=Number(saved.zoom)||100,theme=saved.theme==='dark'?'dark':'light',lineRows=[],resizeTimer=0,quietTimer=0,wheelActive=false,wheelDirection=0,hideHintTimer=0,logicalWidth=900;
  function persist(){try{localStorage.setItem(docKey,JSON.stringify({...saved,zoom,theme}));}catch(_){} }
  document.body.dataset.theme=theme;
  function updateThemeLabel(){themeButton.textContent=theme==='dark'?'☼ Light':'☾ Dark';themeButton.setAttribute('aria-pressed',String(theme==='dark'));themeButton.setAttribute('aria-label','Switch to '+(theme==='dark'?'light':'dark')+' reader theme');}
  function syncFrame(){const scale=zoom/100;stage.style.transform='scale('+scale+')';frame.style.width=(logicalWidth*scale)+'px';frame.style.height=(paper.scrollHeight*scale)+'px';}
  function updateLogicalWidth(){const cs=getComputedStyle(viewer),available=viewer.clientWidth-parseFloat(cs.paddingLeft)-parseFloat(cs.paddingRight);logicalWidth=Math.max(280,Math.min(954,available));stage.style.setProperty('--logical-width',logicalWidth+'px');syncFrame();}
  function setZoom(next,keepPosition=true){
    const anchor=keepPosition?firstVisibleAnchor():null;
    zoom=Math.max(60,Math.min(180,Math.round(next/10)*10));syncFrame();
    zoomText.textContent=zoom+'%';zoomText.setAttribute('aria-label','Zoom '+zoom+' percent');persist();
    if(anchor){requestAnimationFrame(()=>{viewer.scrollTop+=anchor.el.getBoundingClientRect().top-anchor.top;});}
  }
  function firstVisibleAnchor(){const nodes=paper.querySelectorAll('h1,h2,h3,p,table,pre');for(const el of nodes){const r=el.getBoundingClientRect();if(r.bottom>viewer.getBoundingClientRect().top+15)return{el,top:r.top};}return null;}
  function applyTheme(next){resetWheelGesture();theme=next;document.body.dataset.theme=theme;updateThemeLabel();persist();}
  themeButton.addEventListener('click',()=>applyTheme(theme==='dark'?'light':'dark'));
  function resetWheelGesture(){clearTimeout(quietTimer);quietTimer=0;wheelActive=false;wheelDirection=0;}
  function manualZoom(next){resetWheelGesture();setZoom(next);}
  zoomIn.addEventListener('click',()=>manualZoom(zoom+10));zoomOut.addEventListener('click',()=>manualZoom(zoom-10));zoomReset.addEventListener('click',()=>manualZoom(100));
  updateLogicalWidth();setZoom(zoom,false);updateThemeLabel();
  document.addEventListener('wheel',e=>{
    if(!e.ctrlKey||e.deltaY===0){if(!e.ctrlKey)resetWheelGesture();return;}
    if(e.cancelable)e.preventDefault();
    const direction=Math.sign(e.deltaY);
    if(!wheelActive){wheelActive=true;wheelDirection=direction;setZoom(zoom-(direction*10));}
    else if(direction!==wheelDirection){wheelDirection=direction;setZoom(zoom-(direction*10));}
    clearTimeout(quietTimer);quietTimer=setTimeout(resetWheelGesture,160);
  },{passive:false,capture:true});
  document.addEventListener('keyup',e=>{if(e.key==='Control')resetWheelGesture();});
  window.addEventListener('blur',resetWheelGesture);

  function visible(node){for(let el=node.parentElement;el&&el!==paper;el=el.parentElement){if(el.hidden||el.getAttribute('aria-hidden')==='true')return false;if(el.tagName==='DETAILS'&&!el.open&&node.parentElement!==el.querySelector('summary')&&!el.querySelector('summary')?.contains(node))return false;const s=getComputedStyle(el);if(s.display==='none'||s.visibility==='hidden')return false;}return true;}
  function ownerFor(node){const el=node.parentElement,spatial=el.closest('[data-spatial-owner]'),block=el.closest('[data-reading-block]');if(spatial)return'spatial:'+spatial.dataset.spatialOwner;const heading=el.closest('.section-heading');if(heading){if(!heading.dataset.spatialOwner){const section=heading.closest('section');heading.dataset.spatialOwner='section-heading-'+(section?.id||'unnamed');}return'spatial:'+heading.dataset.spatialOwner;}const row=el.closest('tr');if(row){if(!row.dataset.spatialOwner){const rowIndex=Array.from(row.parentElement.children).indexOf(row);row.dataset.spatialOwner=(block?.dataset.readingBlock||'paper')+'-table-row-'+rowIndex;}return'spatial:'+row.dataset.spatialOwner;}return block?.dataset.readingBlock||'paper';}
  function groupSpatialFragments(fragments){
    const owners=new Map();
    for(const fragment of fragments){if(!Number.isFinite(fragment.t)||!Number.isFinite(fragment.b)||fragment.b-fragment.t<=.1)continue;const source=fragment.source||'spatial';if(!owners.has(source))owners.set(source,[]);owners.get(source).push(fragment);}
    const grouped=[];
    for(const [source,owned] of owners){
      const rows=[];
      const sorted=owned.sort((a,b)=>a.t-b.t||a.b-b.b);
      for(const r of sorted){
        const band={t:r.t,b:r.b};let merged=true;
        while(merged){merged=false;for(let i=rows.length-1;i>=0;i--){const row=rows[i];if(Math.min(row.b,band.b)-Math.max(row.t,band.t)>.1){band.t=Math.min(band.t,row.t);band.b=Math.max(band.b,row.b);rows.splice(i,1);merged=true;}}}
        rows.push(band);
      }
      grouped.push(...rows.map(row=>({...row,c:(row.t+row.b)/2,h:row.b-row.t,source})));
    }
    return grouped;
  }
  function rebuildLines(){
    if(!paper.isConnected)return;
    gutter.replaceChildren();paper.querySelector('.hover-band')?.remove();
    const band=document.createElement('div');band.className='hover-band';band.hidden=true;paper.prepend(band);
    const ptop=paper.getBoundingClientRect().top,scale=zoom/100,walker=document.createTreeWalker(paper,NodeFilter.SHOW_TEXT);let node,fragments=[],spatialFragments=[];
    while((node=walker.nextNode())){
      if(!node.nodeValue||!node.nodeValue.trim()||!visible(node)||node.parentElement.closest('script,style,.line-gutter,.line-hint,.toolbar'))continue;
      const ranges=ScratchLineGeometry.nonWhitespaceRanges(node.nodeValue),source=ownerFor(node);
      for(const [start,end] of ranges){const range=document.createRange();range.setStart(node,start);range.setEnd(node,end);for(const rect of range.getClientRects()){if(rect.width<.1||rect.height<.1)continue;const fragment=ScratchLineGeometry.localFragment(rect,ptop,scale,source);(source.startsWith('spatial:')?spatialFragments:fragments).push(fragment);}}
    }
    lineRows=[...ScratchLineGeometry.groupFragments(fragments),...groupSpatialFragments(spatialFragments)].sort((a,b)=>a.c-b.c||a.source.localeCompare(b.source));const frag=document.createDocumentFragment();
    lineRows.forEach((row,i)=>{const label=document.createElement('span');label.className='line-label';label.dataset.number=String(i+1);label.dataset.index=String(i);label.style.top=row.c+'px';label.title='Rendered line '+(i+1);frag.append(label);});gutter.append(frag);
    gutter.style.height=paper.scrollHeight+'px';gutter.setAttribute('aria-hidden','true');
    gutter.querySelectorAll('.line-label').forEach(label=>{label.addEventListener('pointerenter',()=>showLine(Number(label.dataset.index),label));label.addEventListener('pointerleave',clearLine);});
  }
  function showLine(index,label){const row=lineRows[index];if(!row)return;const band=paper.querySelector('.hover-band');band.hidden=false;band.style.top=row.t+'px';band.style.height=Math.max(row.h,13)+'px';hint.textContent='Rendered line '+(index+1);hint.classList.add('visible');clearTimeout(hideHintTimer);}
  function clearLine(){const band=paper.querySelector('.hover-band');if(band)band.hidden=true;hideHintTimer=setTimeout(()=>hint.classList.remove('visible'),120);}
  function scheduleLines(){clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{updateLogicalWidth();syncFrame();rebuildLines();},90);}
  if('ResizeObserver'in window){new ResizeObserver(scheduleLines).observe(paper);}else window.addEventListener('resize',scheduleLines);
  document.fonts?.ready.then(scheduleLines);paper.addEventListener('toggle',scheduleLines,true);window.addEventListener('resize',scheduleLines);viewer.addEventListener('scroll',clearLine,{passive:true});document.addEventListener('selectionchange',clearLine);
  rebuildLines();

  let pan=null;
  viewer.addEventListener('pointerdown',e=>{if(!e.metaKey||e.ctrlKey||e.button!==0||e.target.closest('a,button,input,textarea,select,summary,[contenteditable="true"]'))return;pan={x:e.clientX,y:e.clientY,left:viewer.scrollLeft,top:viewer.scrollTop,moved:false,captured:false,id:e.pointerId};viewer.classList.add('drag-ready');});
  viewer.addEventListener('pointermove',e=>{if(!pan||e.pointerId!==pan.id)return;const dx=e.clientX-pan.x,dy=e.clientY-pan.y;if(!pan.moved&&Math.hypot(dx,dy)<5)return;if(!pan.captured){pan.moved=true;pan.captured=true;try{viewer.setPointerCapture(e.pointerId);}catch(_){} }e.preventDefault();viewer.classList.remove('drag-ready');viewer.classList.add('dragging');viewer.scrollLeft=pan.left-dx;viewer.scrollTop=pan.top-dy;});
  function endPan(e){if(!pan)return;const active=pan;pan=null;viewer.classList.remove('dragging','drag-ready');if(active.captured&&viewer.hasPointerCapture?.(active.id)){try{viewer.releasePointerCapture(active.id);}catch(_){}}}
  viewer.addEventListener('pointerup',endPan);viewer.addEventListener('pointercancel',endPan);viewer.addEventListener('lostpointercapture',endPan);window.addEventListener('blur',endPan);
  viewer.addEventListener('click',e=>{if(e.target.closest('a[href^="#"]')){const id=decodeURIComponent(e.target.closest('a').getAttribute('href').slice(1));setTimeout(()=>history.replaceState(null,'','#'+encodeURIComponent(id)),0);}});

  const restore=()=>{if(location.hash){const id=decodeURIComponent(location.hash.slice(1));document.getElementById(id)?.scrollIntoView({block:'start'});return;}const id=saved.anchor;if(id){const el=document.getElementById(id);if(el){const desired=viewer.getBoundingClientRect().top+(Number(saved.offset)||0);viewer.scrollTop+=el.getBoundingClientRect().top-desired;}else if(Number.isFinite(saved.scrollTop))viewer.scrollTop=saved.scrollTop;}else if(Number.isFinite(saved.scrollTop))viewer.scrollTop=saved.scrollTop;};
  requestAnimationFrame(()=>requestAnimationFrame(restore));
  let saveTimer=0;viewer.addEventListener('scroll',()=>{clearTimeout(saveTimer);saveTimer=setTimeout(()=>{const top=viewer.getBoundingClientRect().top+30;const blocks=[...paper.querySelectorAll('.reading-block')];const active=blocks.findLast?blocks.findLast(el=>el.getBoundingClientRect().top<=top):blocks.slice().reverse().find(el=>el.getBoundingClientRect().top<=top);saved.anchor=active?.id||'';saved.offset=active?active.getBoundingClientRect().top-viewer.getBoundingClientRect().top:viewer.scrollTop;saved.scrollTop=viewer.scrollTop;persist();},170);},{passive:true});
  window.addEventListener('hashchange',()=>{const el=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(el)el.scrollIntoView({block:'start'});});
  window.addEventListener('beforeprint',()=>clearLine());
})();
