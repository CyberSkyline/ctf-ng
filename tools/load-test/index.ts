import http from 'k6/http';
import exec from 'k6/execution';
import { browser } from 'k6/browser';
import { sleep, check, fail } from 'k6';

const BASE_URL = 'http://127.0.0.1';
const STAGE_ONE_VUS = Number(__ENV.STAGE_ONE_VUS) || 2;
const STAGE_TWO_VUS = Number(__ENV.STAGE_TWO_VUS) || 5;
const STAGE_THREE_VUS = Number(__ENV.STAGE_THREE_VUS) || 10;

export const options = {
  scenarios: {
    load_test: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: STAGE_ONE_VUS }, // ramp to STAGE_ONE_VUS
        { duration: '1m', target: STAGE_TWO_VUS },  // ramp to STAGE_TWO_VUS
        { duration: '30s', target: STAGE_THREE_VUS },   // ramp to STAGE_THREE_VUS
      ],
      gracefulRampDown: '30s',
    },
  },
};

export function setup() {
  let res = http.get(BASE_URL);
  if (res.status !== 200) {
    exec.test.abort(`Got unexpected status code ${res.status} when trying to setup. Exiting.`);
  }
}

// The default exported function is gonna be picked up by k6 as the entry point for the test script. It will be executed repeatedly in "iterations" for the whole duration of the test.
export default async function () {
  // Make a GET request to the target URL
  http.get('http://localhost');

  // Sleep for 1 second to simulate real-world usage
  sleep(1);
}