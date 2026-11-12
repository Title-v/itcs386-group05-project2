// Shared settings for every k6 test: target URLs, think time, QUICK mode and the summary writer.
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.2/index.js';

export const SHOP = (__ENV.BASE_URL || 'http://157.85.102.236/shop').replace(/\/$/, '');
export const API = `${SHOP}/wp-json/wc/store/v1`;
export const QUICK = __ENV.QUICK === '1' || __ENV.QUICK === 'true';

// Think time between page views, in seconds. Real shoppers read a page before clicking again.
export const THINK_MIN = 1;
export const THINK_MAX = QUICK ? 2 : 4;

function toSeconds(duration) {
  const units = { h: 3600, m: 60, s: 1 };
  const pattern = /(\d+(?:\.\d+)?)([hms])/g;
  let total = 0;
  let part;
  while ((part = pattern.exec(duration)) !== null) total += Number(part[1]) * units[part[2]];
  return total;
}

// QUICK=1 shrinks every stage to a tenth of its length (at least 5 s) for demos and smoke checks.
// The VU targets stay the same, so the load shape is unchanged; only the time is shorter.
export function scaleStages(stages) {
  if (!QUICK) return stages;
  return stages.map((s) => Object.assign({}, s, { duration: `${Math.max(5, Math.round(toSeconds(s.duration) / 10))}s` }));
}

export function totalDuration(stages) {
  const seconds = stages.reduce((sum, s) => sum + toSeconds(s.duration), 0);
  return `${Math.floor(seconds / 60)}m${Math.round(seconds % 60)}s`;
}

// Per-endpoint sub-metrics get the same response-time limit as the whole test, so the end-of-test
// summary shows a breakdown for each step of the shopper journey.
export const ENDPOINTS = ['home', 'categories', 'list', 'search', 'detail', 'cart_get', 'cart_add', 'cart_update', 'cart_remove'];

export function endpointThresholds(limit) {
  const result = {};
  for (const e of ENDPOINTS) result[`http_req_duration{endpoint:${e}}`] = [limit];
  return result;
}

function stamp(date, offsetHours, suffix) {
  return new Date(date.getTime() + offsetHours * 3600 * 1000).toISOString().replace('Z', suffix);
}

// Writes summary.txt and summary.json (with run date and time) into OUT_DIR, and prints the summary.
export function makeHandleSummary(testName, options) {
  return function handleSummary(data) {
    const ended = new Date();
    const started = new Date(ended.getTime() - data.state.testRunDurationMs);
    const meta = {
      test: testName,
      base_url: SHOP,
      quick_mode: QUICK,
      started_utc: started.toISOString(),
      ended_utc: ended.toISOString(),
      started_bangkok: stamp(started, 7, '+07:00'),
      ended_bangkok: stamp(ended, 7, '+07:00'),
      planned_duration: totalDuration(options.stages),
      stages: options.stages,
      thresholds: options.thresholds,
    };
    const header =
      `Test: ${testName}${QUICK ? ' (QUICK mode)' : ''}\n` +
      `Target: ${SHOP}\n` +
      `Started: ${meta.started_bangkok} (Bangkok)  Ended: ${meta.ended_bangkok}\n\n`;
    const outDir = __ENV.OUT_DIR || 'results';
    const name = __ENV.OUT_DIR ? 'summary' : `${testName}-${started.toISOString().replace(/[:.]/g, '-')}-summary`;
    return {
      stdout: header + textSummary(data, { indent: ' ', enableColors: true }),
      [`${outDir}/${name}.txt`]: header + textSummary(data, { indent: ' ', enableColors: false }),
      [`${outDir}/${name}.json`]: JSON.stringify(Object.assign({ meta }, data), null, 2),
    };
  };
}
