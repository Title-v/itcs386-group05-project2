/* Geometry only: no content edits, DOM wrapping, or browser state. */
(function(root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.ScratchLineGeometry = api;
})(typeof globalThis === 'object' ? globalThis : this, function() {
  'use strict';
  function nonWhitespaceRanges(text) {
    return Array.from(text.matchAll(/\S+/gu), m => [m.index, m.index + m[0].length]);
  }
  function localFragment(rect, originTop, scale, source) {
    return {t:(rect.top-originTop)/scale, b:(rect.bottom-originTop)/scale, source};
  }
  function groupFragments(fragments) {
    const sorted = fragments.filter(r => Number.isFinite(r.t) && Number.isFinite(r.b) && r.b-r.t > .1)
      .map(r => ({...r, source:r.source || r.id || '', h:r.b-r.t, c:(r.t+r.b)/2}))
      .sort((a,b) => a.t-b.t || b.h-a.h || a.source.localeCompare(b.source));
    const rows = [];
    for (const r of sorted) {
      let best = null, bestScore = -Infinity;
      for (let i=rows.length-1;i>=0;i--) {
        const row = rows[i];
        if (row.source !== r.source) continue;
        const overlap = Math.min(row.coreB,r.b)-Math.max(row.coreT,r.t);
        const ratio = overlap/Math.min(row.coreB-row.coreT,r.h);
        if (overlap <= .1 || ratio < .5) continue;
        const score = ratio-Math.abs((row.coreT+row.coreB)/2-r.c)*.001;
        if (score > bestScore) { best=row; bestScore=score; }
      }
      if (!best) rows.push({t:r.t,b:r.b,coreT:r.t,coreB:r.b,source:r.source});
      else { best.t=Math.min(best.t,r.t); best.b=Math.max(best.b,r.b); best.coreT=Math.max(best.coreT,r.t); best.coreB=Math.min(best.coreB,r.b); }
    }
    return rows.sort((a,b)=>(a.t+a.b)-(b.t+b.b) || a.source.localeCompare(b.source))
      .map(({t,b,source})=>({t,b,c:(t+b)/2,h:b-t,source}));
  }
  return Object.freeze({groupFragments, nonWhitespaceRanges, localFragment});
});
