// Goal: raise the number of shoppers step by step (10 -> 50) to find the load at which
// response time or the error rate starts to go wrong.
import { scaleStages, endpointThresholds, makeHandleSummary } from './lib/config.js';
import { discoverCatalog, shopperVisit } from './lib/shopper.js';

export const options = {
  stages: scaleStages([
    { duration: '1m', target: 10 }, // step 1: normal load
    { duration: '2m', target: 10 },
    { duration: '1m', target: 20 }, // step 2: 2x normal
    { duration: '2m', target: 20 },
    { duration: '1m', target: 30 }, // step 3: 3x normal
    { duration: '2m', target: 30 },
    { duration: '1m', target: 40 }, // step 4: 4x normal
    { duration: '2m', target: 40 },
    { duration: '1m', target: 50 }, // step 5: 5x normal
    { duration: '2m', target: 50 },
    { duration: '2m', target: 0 }, // recovery
  ]),
  thresholds: Object.assign(
    {
      http_req_duration: ['p(95)<2000'],
      http_req_failed: [
        'rate<0.05',
        // The server is shared by every group: stop early if a third of requests are failing.
        { threshold: 'rate<0.30', abortOnFail: true, delayAbortEval: '1m' },
      ],
      checks: ['rate>0.95'],
    },
    endpointThresholds('p(95)<2000'),
  ),
};

export function setup() {
  return discoverCatalog();
}

export default function (catalog) {
  shopperVisit(catalog);
}

export const handleSummary = makeHandleSummary('stress', options);
