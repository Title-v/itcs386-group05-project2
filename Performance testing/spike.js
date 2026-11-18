// Goal: jump from 5 to 50 shoppers in 20 s (for example a flash sale), then drop back,
// and measure how long the shop takes to return to normal response times.
import { scaleStages, endpointThresholds, makeHandleSummary } from './lib/config.js';
import { discoverCatalog, shopperVisit } from './lib/shopper.js';

export const options = {
  stages: scaleStages([
    { duration: '30s', target: 5 }, // warm up
    { duration: '2m', target: 5 }, // baseline: normal response time to compare against
    { duration: '20s', target: 50 }, // spike up (10x)
    { duration: '1m', target: 50 }, // hold the spike
    { duration: '20s', target: 5 }, // spike ends
    { duration: '5m', target: 5 }, // recovery window: how long until it is back to baseline?
    { duration: '30s', target: 0 }, // ramp down
  ]),
  thresholds: Object.assign(
    {
      http_req_duration: ['p(95)<3000'],
      http_req_failed: [
        'rate<0.10',
        // The server is shared by every group: stop early if half of all requests are failing.
        { threshold: 'rate<0.50', abortOnFail: true, delayAbortEval: '30s' },
      ],
      checks: ['rate>0.90'],
    },
    endpointThresholds('p(95)<3000'),
  ),
};

export function setup() {
  return discoverCatalog();
}

export default function (catalog) {
  shopperVisit(catalog);
}

export const handleSummary = makeHandleSummary('spike', options);
