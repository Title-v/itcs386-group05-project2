// Goal: keep normal load (10 shoppers) running for an hour to see whether response time or
// the error rate gets worse over time (memory leaks, growing session tables, full logs).
import { scaleStages, endpointThresholds, makeHandleSummary } from './lib/config.js';
import { discoverCatalog, shopperVisit } from './lib/shopper.js';

// SOAK_HOLD changes the length of the steady part, for example -e SOAK_HOLD=90m.
const HOLD = __ENV.SOAK_HOLD || '60m';

export const options = {
  stages: scaleStages([
    { duration: '2m', target: 10 }, // ramp up
    { duration: HOLD, target: 10 }, // long steady load
    { duration: '2m', target: 0 }, // ramp down
  ]),
  thresholds: Object.assign(
    {
      http_req_duration: ['p(95)<1000', 'p(99)<2000'],
      http_req_failed: ['rate<0.01'],
      checks: ['rate>0.99'],
    },
    endpointThresholds('p(95)<1000'),
  ),
};

export function setup() {
  return discoverCatalog();
}

export default function (catalog) {
  shopperVisit(catalog);
}

export const handleSummary = makeHandleSummary('soak', options);
