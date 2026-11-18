// Goal: check that the shop serves a normal day's traffic (10 shoppers browsing at once)
// with 95% of responses under 1 s and almost no errors.
import { scaleStages, endpointThresholds, makeHandleSummary } from './lib/config.js';
import { discoverCatalog, shopperVisit } from './lib/shopper.js';

export const options = {
  stages: scaleStages([
    { duration: '2m', target: 10 }, // ramp up to normal load
    { duration: '6m', target: 10 }, // hold normal load
    { duration: '1m', target: 0 }, // ramp down
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

export const handleSummary = makeHandleSummary('average-load', options);
