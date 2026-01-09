import http from 'k6/http';
import exec from 'k6/execution';
import { SharedArray } from 'k6/data';
import { sleep } from 'k6';
import { make_user, User } from './model/user.ts';
import { DefaultHttpUserScenario } from './scenarios/default_http_user.ts';

const BASE_URL = __ENV.BASE_URL || 'http://localhost';
const STAGE_ONE_DURATION = __ENV.STAGE_ONE_DURATION || '5s';
const STAGE_TWO_DURATION = __ENV.STAGE_TWO_DURATION || '10s';
const STAGE_THREE_DURATION = __ENV.STAGE_THREE_DURATION || '5s';
const STAGE_ONE_VUS = Number(__ENV.STAGE_ONE_VUS) || 2;
const STAGE_TWO_VUS = Number(__ENV.STAGE_TWO_VUS) || 5;
const STAGE_THREE_VUS = Number(__ENV.STAGE_THREE_VUS) || 10;

const eventId = JSON.parse(open('./data.json'))['event_id'];
if (!eventId) {
  throw new Error('event_id key missing in data.json');
}

const challengeId = JSON.parse(open('./data.json'))['challenge_id'];
if (!challengeId) {
  throw new Error('challenge_id key missing in data.json');
}

const questionId = JSON.parse(open('./data.json'))['question_id'];
if (!questionId) {
  throw new Error('question_id key missing in data.json');
}

const adminUsers: User[] = new SharedArray('adminUsers', function () {
  const data = JSON.parse(open('./data.json'))['admins'];
  if (!Array.isArray(data)) {
    throw new Error('admins key in data.json must be an array');
  }

  return data.map((u: any, i: number) => make_user(i, u.email, u.password, BASE_URL, 'admin'));
});

const defaultUsers: User[] = new SharedArray('defaultUsers', function () {
  const data = JSON.parse(open('./data.json'))['users'];
  if (!Array.isArray(data)) {
    throw new Error('users key in data.json must be an array');
  }

  return data.map((u: any, i: number) => make_user(i, u.email, u.password, BASE_URL));
});

export const options = {
  insecureSkipTLSVerify: true,
  scenarios: {
    defaultHttpUser: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: STAGE_ONE_DURATION, target: STAGE_ONE_VUS }, // ramp to STAGE_ONE_VUS
        { duration: STAGE_TWO_DURATION, target: STAGE_TWO_VUS },  // ramp to STAGE_TWO_VUS
        { duration: STAGE_THREE_DURATION, target: STAGE_THREE_VUS },   // ramp to STAGE_THREE_VUS
      ],
      gracefulRampDown: '30s',
      exec: 'defaultHttpUser',
    },
    // defaultBrowserUser: {
    //   executor: 'ramping-vus',
    //   options: {
    //     browser: {
    //       type: 'chromium',
    //     },
    //   },
    //   startVUs: 0,
    //   stages: [
    //     { duration: '30s', target: Math.ceil(STAGE_ONE_VUS / 10) }, // ramp to STAGE_ONE_VUS
    //     { duration: '1m', target: Math.ceil(STAGE_TWO_VUS / 10) },  // ramp to STAGE_TWO_VUS
    //     { duration: '30s', target: Math.ceil(STAGE_THREE_VUS / 10) },   // ramp to STAGE_THREE_VUS
    //   ],
    //   gracefulRampDown: '30s',
    //   exec: 'defaultBrowserUser',
    // },
    // badActor: {
    //   executor: 'ramping-vus',
    //   options: {
    //     browser: {
    //       type: 'chromium',
    //     },
    //   },
    //   startVUs: 0,
    //   stages: [
    //     { duration: '30s', target: Math.ceil(STAGE_ONE_VUS / 10) }, // ramp to STAGE_ONE_VUS
    //     { duration: '1m', target: Math.ceil(STAGE_TWO_VUS / 10) },  // ramp to STAGE_TWO_VUS
    //     { duration: '30s', target: Math.ceil(STAGE_THREE_VUS / 10) },   // ramp to STAGE_THREE_VUS
    //   ],
    //   gracefulRampDown: '30s',
    //   exec: 'badActor',
    // },
    // adminUser: {
    //   executor: 'ramping-vus',
    //   options: {
    //     browser: {
    //       type: 'chromium',
    //     },
    //   },
    //   startVUs: 0,
    //   stages: [
    //     { duration: '30s', target: Math.ceil(STAGE_ONE_VUS / 10) }, // ramp to STAGE_ONE_VUS
    //     { duration: '1m', target: Math.ceil(STAGE_TWO_VUS / 10) },  // ramp to STAGE_TWO_VUS
    //     { duration: '30s', target: Math.ceil(STAGE_THREE_VUS / 10) },   // ramp to STAGE_THREE_VUS
    //   ],
    //   gracefulRampDown: '30s',
    //   exec: 'adminUser',
    // },
  },
};

export function setup() {
  let res = http.get(BASE_URL);
  if (res.status !== 200) {
    exec.test.abort(`Got unexpected status code ${res.status} when trying to setup. Exiting.`);
  }
}

function getDefaultUser() {
  return defaultUsers[exec.scenario.iterationInTest % defaultUsers.length];
}

// The default exported function is gonna be picked up by k6 as the entry point for the test script. It will be executed repeatedly in "iterations" for the whole duration of the test.
export async function defaultHttpUser() {
  let user = getDefaultUser();
  let scenario = new DefaultHttpUserScenario(user, eventId, challengeId, questionId);
  scenario.execute();
  sleep(1);
}

// export async function defaultBrowserUser() {
//   let user = getDefaultUser();
//   let session = await UserBrowserSession.make(user, browser);
//   await defaultUserScenario(session);
//   sleep(1);
// }

// function getCurrentBadActor() {
//   return badActors[exec.scenario.iterationInInstance % badActors.length];
// }

// export async function badActor() {
//   let user = getCurrentBadActor();
//   // Make a GET request to the target URL
//   for (let i = 0; i<1000; i++) {
//     http.get(BASE_URL);
//   }

//   sleep(1);
// }

// function getCurrentAdminUser() {
//   return adminUsers[exec.scenario.iterationInInstance % adminUsers.length];
// }

// export async function adminUser() {
//   let user = getCurrentAdminUser();
//   // Make a GET request to the target URL
//   http.get(BASE_URL);
//   sleep(1);
// }
