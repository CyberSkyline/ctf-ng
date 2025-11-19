import http from 'k6/http';
import exec from 'k6/execution';
import { SharedArray } from 'k6/data';
import { browser } from 'k6/browser';
import { sleep, check, fail } from 'k6';
import { make_user, make_session, User } from './user.ts';

const BASE_URL = __ENV.BASE_URL || 'http://localhost';
const STAGE_ONE_VUS = Number(__ENV.STAGE_ONE_VUS) || 2;
const STAGE_TWO_VUS = Number(__ENV.STAGE_TWO_VUS) || 5;
const STAGE_THREE_VUS = Number(__ENV.STAGE_THREE_VUS) || 10;

const adminUsers: User[] = new SharedArray('adminUsers', function () {
  return [...Array(5).keys()].map(i => make_user(i, 'admin'));
});

const defaultUsers: User[] = new SharedArray('defaultUsers', function () {
  return [...Array(500).keys()].slice(10).map(i => make_user(i));
});

const badActors: User[] = new SharedArray('badActors', function () {
  return [...Array(10).keys()].map(i => make_user(i));
});

export const options = {
  scenarios: {
    defaultUser: {
      executor: 'ramping-vus',
      options: {
        browser: {
          type: 'chromium',
        },
      },
      startVUs: 0,
      stages: [
        { duration: '30s', target: STAGE_ONE_VUS }, // ramp to STAGE_ONE_VUS
        { duration: '1m', target: STAGE_TWO_VUS },  // ramp to STAGE_TWO_VUS
        { duration: '30s', target: STAGE_THREE_VUS },   // ramp to STAGE_THREE_VUS
      ],
      gracefulRampDown: '30s',
      exec: 'defaultUser',
    },
    badActor: {
      executor: 'ramping-vus',
      options: {
        browser: {
          type: 'chromium',
        },
      },
      startVUs: 0,
      stages: [
        { duration: '30s', target: Math.ceil(STAGE_ONE_VUS / 10) }, // ramp to STAGE_ONE_VUS
        { duration: '1m', target: Math.ceil(STAGE_TWO_VUS / 10) },  // ramp to STAGE_TWO_VUS
        { duration: '30s', target: Math.ceil(STAGE_THREE_VUS / 10) },   // ramp to STAGE_THREE_VUS
      ],
      gracefulRampDown: '30s',
      exec: 'badActor',
    },
    adminUser: {
      executor: 'ramping-vus',
      options: {
        browser: {
          type: 'chromium',
        },
      },
      startVUs: 0,
      stages: [
        { duration: '30s', target: Math.ceil(STAGE_ONE_VUS / 10) }, // ramp to STAGE_ONE_VUS
        { duration: '1m', target: Math.ceil(STAGE_TWO_VUS / 10) },  // ramp to STAGE_TWO_VUS
        { duration: '30s', target: Math.ceil(STAGE_THREE_VUS / 10) },   // ramp to STAGE_THREE_VUS
      ],
      gracefulRampDown: '30s',
      exec: 'adminUser',
    },
  },
};

export function setup() {
  let res = http.get(BASE_URL);
  if (res.status !== 200) {
    exec.test.abort(`Got unexpected status code ${res.status} when trying to setup. Exiting.`);
  }
}

function getDefaultUser() {
  return defaultUsers[exec.scenario.iterationInInstance % defaultUsers.length];
}

// The default exported function is gonna be picked up by k6 as the entry point for the test script. It will be executed repeatedly in "iterations" for the whole duration of the test.
export async function defaultUser() {
  let user = await make_session(getDefaultUser(), browser);
  // Make a GET request to the target URL
  await user.login();
  sleep(1);
}

function getCurrentBadActor() {
  return badActors[exec.scenario.iterationInInstance % badActors.length];
}

export async function badActor() {
  let user = getCurrentBadActor();
  // Make a GET request to the target URL
  for (let i = 0; i<1000; i++) {
    http.get(BASE_URL);
  }

  sleep(1);
}

function getCurrentAdminUser() {
  return adminUsers[exec.scenario.iterationInInstance % adminUsers.length];
}

export async function adminUser() {
  let user = getCurrentAdminUser();
  // Make a GET request to the target URL
  http.get(BASE_URL);
  sleep(1);
}
