import http from 'k6/http';
import { check, sleep } from 'k6';
import { User } from "../model/user.ts";

// visit challenge


// start challenge

// solve challenge

// Submit challenge

// challenge flow

// leaderboard flow

// join team

// leave team

// change captain

// remove player

// add player

// team flow

// create ticket

// comment on ticket

// resolve ticket

// Logout

// user flow
export class DefaultHttpUserScenario {
    
    user: User;
    params: http.Params;

    constructor(user: User) {
        this.user = user;
        this.params = {
            headers: {},
            cookies: {},
        };
    }

    url(path: string): string {
        return `${this.user.base_url}${path}`;
    }

    post(path: string, body: any) {
        console.log(`POST ${this.url(path)} with body: ${JSON.stringify(body)} and params: ${JSON.stringify(this.params)}`);
        const res = http.post(this.url(path), JSON.stringify(body), this.params);
        console.log(`POST response: ${JSON.stringify(res)}`);
        return res;
    }

    put(path: string, body: any) {
        console.log(`PUT ${this.url(path)} with body: ${JSON.stringify(body)} and params: ${JSON.stringify(this.params)}`);
        const res = http.put(this.url(path), JSON.stringify(body), this.params);
        console.log(`PUT response: ${JSON.stringify(res)}`);
        return res;
    }

    get(path: string) {
        console.log(`GET ${this.url(path)}`);
        const res = http.get(this.url(path), this.params);
        console.log(`GET response: ${JSON.stringify(res)}`);
        return res;
    }

    update_csrf_token() {
        // console.log(`Logging in user ${this.user.email} with password ${this.user.password}`);
        const basePageRes = this.get('/');

        check(basePageRes, { "base page status equals 200": (r) => r.status === 200 });
        const csrfTokenRegex = /csrfToken: '(?<csrfToken>[a-f0-9]{64})'/;

        // csrfToken: 'c203fe62501ea33def88df7e12265a3e1af04ee76d4b3926c98d64fab86b6dd1',
        if (basePageRes.body == null) {
            return;
        }

        const regexResult = csrfTokenRegex.exec(basePageRes.body.toString());
        if (regexResult == null) {
            console.error(`Regex Search Failed`);
            console.error(basePageRes.body.toString());
            return;
        }
        this.params.headers!['CSRF-Token'] = regexResult[1];
    }

    login() {
        this.update_csrf_token();
        this.params.headers!['Content-Type'] = 'application/json';
        console.log(`Extracted CSRF Token: ${this.params.headers!['CSRF-Token']}`);
        
        const loginRes = this.post('/ng/users/login', {
            username: this.user.email,
            password: this.user.password,
        });

        check(loginRes, { "login status equals 200": (r) => r.status === 200 });
        check(loginRes, { "login success": (r) => r.json('success') === true });
        console.log(`Login response: ${loginRes.body}`);

        this.update_csrf_token();
    }

    select_sponsor() {
        const sponsorRes = this.put('/ng/users/me/sponsor', {
            sponsor_id: 1
        });
        check(sponsorRes, { "select sponsor status equals 200": (r) => r.status === 200 });
        check(sponsorRes, { "select sponsor success": (r) => r.json('success') === true });
        check(sponsorRes, { "select sponsor correct sponsor": (r) => r.json('data.name') === "sample sponsor" });
    }

    dashboard() {
        const dashboardRes = this.get('/');
        check(dashboardRes, { "dashboard status equals 200": (r) => r.status === 200 });
    }

    is_registered(eventNumber: number): boolean {
        const res = this.get(`/ng/users/me/teams`);
        check(res, { [`teams status equals 200`]: (r) => r.status === 200 });
        const eventIds = res.json("data.#.event_id");
        if (!Array.isArray(eventIds)) {
            return false;
        }

        return eventIds.includes(eventNumber);
    }

    register_event(eventNumber: number) {
        if (this.is_registered(eventNumber)) {
            return;
        }
        const resBeforeRegister = this.get(`/events/${eventNumber}`);
        check(resBeforeRegister, { [`event ${eventNumber} status before register equals 200`]: (r) => r.status === 200 });

        const registerRes = this.post(`/ng/events/${eventNumber}/me/register`, {
            team_name: `lt${this.user.id}_team`,
        });
        check(registerRes, { [`event ${eventNumber} register status equals 201`]: (r) => r.status === 201 });

        const resAfterRegister = this.get(`/events/${eventNumber}`);
        check(resAfterRegister, { [`event ${eventNumber} status after register equals 200`]: (r) => r.status === 200 });
    }

    is_event_started(eventNumber: number): boolean {
        const res = this.get(`/ng/users/me/teams`);
        check(res, { [`teams status equals 200`]: (r) => r.status === 200 });

        return res.json(`data.#(event_id==${eventNumber})#.start_timestamp`) !== null;
    }

    start_event(eventNumber: number) {
        if (this.is_event_started(eventNumber)) {
            return;
        }
        const resBeforeStart = this.get(`/events/${eventNumber}`);
        check(resBeforeStart, { [`event ${eventNumber} status before start equals 200`]: (r) => r.status === 200 });

        const startRes = this.post(`/ng/events/${eventNumber}/me/team/start`, {});
        check(startRes, { [`event ${eventNumber} start status equals 200`]: (r) => r.status === 200 });

        const resAfterStart = this.get(`/events/${eventNumber}`);
        check(resAfterStart, { [`event ${eventNumber} status after start equals 200`]: (r) => r.status === 200 });
    }

    is_challenge_started(challengeNumber: number): boolean {
        const res = this.get(`/ng/container/me/current_challenge`);
        check(res, { [`current_challenge status equals 200`]: (r) => r.status === 200 });
        check(res, { [`current_challenge success is true`]: (r) => r.json('success') === true });
        return res.json('data') === challengeNumber;
    }

    start_basic_challenge(eventNumber: number, challengeNumber: number) {
        if (this.is_challenge_started(challengeNumber)) {
            return;
        }
        const resBeforeStart = this.get(`/events/${eventNumber}/challenge/${challengeNumber}`);
        check(resBeforeStart, { [`event ${eventNumber} challenge ${challengeNumber} status before start equals 200`]: (r) => r.status === 200 });

        const startRes = this.post(`/ng/events/${eventNumber}/challenge/${challengeNumber}/containers`, {});
        check(startRes, { [`event ${eventNumber} challenge ${challengeNumber} start status equals 200`]: (r) => r.status === 200 });

        const resAfterStart = this.get(`/events/${eventNumber}/challenge/${challengeNumber}`);
        check(resAfterStart, { [`event ${eventNumber} challenge ${challengeNumber} status after start equals 200`]: (r) => r.status === 200 });
    }

    answer_basic_challenge(eventNumber: number, challengeNumber: number, questionNumber: number, correct: boolean) {
        if (correct) {
            const answerRes = this.post(`/ng/events/${eventNumber}/challenges/${challengeNumber}/questions/${questionNumber}/submit`, {
                submission: 'CTF{test_flag}	'
            });
            check(answerRes, { [`event ${eventNumber} challenge ${challengeNumber} question ${questionNumber} correct answer status equals 201`]: (r) => r.status === 201 });
            check(answerRes, { [`event ${eventNumber} challenge ${challengeNumber} question ${questionNumber} correct answer accepted`]: (r) => r.json('data.is_correct') === true });
        } else {
            const answerRes = this.post(`/ng/events/${eventNumber}/challenges/${challengeNumber}/questions/${questionNumber}/submit`, {
                submission: 'wrong_flag'
            });
            check(answerRes, { [`event ${eventNumber} challenge ${challengeNumber} question ${questionNumber} incorrect answer status equals 201`]: (r) => r.status === 201 });
            check(answerRes, { [`event ${eventNumber} challenge ${challengeNumber} question ${questionNumber} incorrect answer rejected`]: (r) => r.json('data.is_correct') === false });
        }
    }

    reset_basic_challenge(eventNumber: number, challengeNumber: number) {
        const resetRes = this.post(`/ng/events/${eventNumber}/challenge/${challengeNumber}/containers/recycle`, {});
        check(resetRes, { [`event ${eventNumber} challenge ${challengeNumber} reset status equals 200`]: (r) => r.status === 200 });
        check(resetRes, { [`event ${eventNumber} challenge ${challengeNumber} reset success`]: (r) => r.json('success') === true });
        check(resetRes, { [`event ${eventNumber} challenge ${challengeNumber} reset new container id`]: (r) => r.json('data') === true });
    }

    execute() {
        this.login();
        this.select_sponsor();
        this.dashboard();
        this.register_event(3);
        this.start_event(3);
        this.start_basic_challenge(3, 3);
        for (let i = 0; i < 10; i++) {
            this.reset_basic_challenge(3, 3);
            sleep(1);
        }

        // await this.answer_basic_challenge(false);
        // sleep(1);
        // await this.answer_basic_challenge(true);
        // sleep(1);
    }
}
