import http from 'k6/http';
import { check, sleep } from 'k6';
import { User } from "../model/user.ts";

export class DefaultHttpUserScenario {
    
    user: User;
    params: http.Params;
    eventId: number; // Add eventId property
    challengeId: number; // Add challengeId property
    questionId: number; // Add questionId property

    constructor(user: User, eventId: number, challengeId: number, questionId: number) {
        this.user = user;
        this.params = {
            headers: {},
            cookies: {},
        };
        this.eventId = eventId; // Store eventId
        this.challengeId = challengeId; // Store challengeId
        this.questionId = questionId; // Store questionId
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
        check(sponsorRes, { "select sponsor correct sponsor": (r) => r.json('data.name') === "Administrative Office of the United States Courts" });
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

    register_event() {
        if (this.is_registered(this.eventId)) {
            return;
        }
        const resBeforeRegister = this.get(`/events/${this.eventId}`);
        check(resBeforeRegister, { [`event ${this.eventId} status before register equals 200`]: (r) => r.status === 200 });

        const registerRes = this.post(`/ng/events/${this.eventId}/me/register`, {
            team_name: `lt${this.user.id}_team`,
        });
        check(registerRes, { [`event ${this.eventId} register status equals 201`]: (r) => r.status === 201 });

        const resAfterRegister = this.get(`/events/${this.eventId}`);
        check(resAfterRegister, { [`event ${this.eventId} status after register equals 200`]: (r) => r.status === 200 });
    }

    is_event_started(eventNumber: number): boolean {
        const res = this.get(`/ng/users/me/teams`);
        check(res, { [`teams status equals 200`]: (r) => r.status === 200 });
        const startTimestamp = res.json(`data.#(event_id==${eventNumber}).start_timestamp`);
        console.log(`Event ${eventNumber} start timestamp: ${JSON.stringify(startTimestamp)}`);
        
        return startTimestamp !== null && startTimestamp !== undefined && startTimestamp !== '';
    }

    start_event() {
        if (this.is_event_started(this.eventId)) {
            console.log(`Event ${this.eventId} has already started.`);
            return;
        }
        const resBeforeStart = this.get(`/events/${this.eventId}`);
        check(resBeforeStart, { [`event ${this.eventId} status before start equals 200`]: (r) => r.status === 200 });

        const startRes = this.post(`/ng/events/${this.eventId}/me/team/start`, {});
        check(startRes, { [`event ${this.eventId} start status equals 200`]: (r) => r.status === 200 });

        const resAfterStart = this.get(`/events/${this.eventId}`);
        check(resAfterStart, { [`event ${this.eventId} status after start equals 200`]: (r) => r.status === 200 });
    }

    is_challenge_started(challengeNumber: number): boolean {
        const res = this.get(`/ng/container/me/current_challenge`);
        check(res, { [`current_challenge status equals 200`]: (r) => r.status === 200 });
        check(res, { [`current_challenge success is true`]: (r) => r.json('success') === true });
        console.log(`Current challenge response: ${res.body}`);
        return res.json('data') === challengeNumber;
    }

    start_basic_challenge() {
        if (this.is_challenge_started(this.challengeId)) {
            return;
        }
        const resBeforeStart = this.get(`/events/${this.eventId}/challenge/${this.challengeId}`);
        check(resBeforeStart, { [`event ${this.eventId} challenge ${this.challengeId} status before start equals 200`]: (r) => r.status === 200 });

        const startRes = this.post(`/ng/events/${this.eventId}/challenge/${this.challengeId}/containers`, {});
        check(startRes, { [`event ${this.eventId} challenge ${this.challengeId} start status equals 200`]: (r) => r.status === 200 });

        const resAfterStart = this.get(`/events/${this.eventId}/challenge/${this.challengeId}`);
        check(resAfterStart, { [`event ${this.eventId} challenge ${this.challengeId} status after start equals 200`]: (r) => r.status === 200 });
    }

    answer_basic_challenge(correct: boolean) {
        if (correct) {
            const answerRes = this.post(`/ng/events/${this.eventId}/challenges/${this.challengeId}/questions/${this.questionId}/submit`, {
                submission: 'CTF{test_flag}	'
            });
            check(answerRes, { [`event ${this.eventId} challenge ${this.challengeId} question ${this.questionId} correct answer status equals 201`]: (r) => r.status === 201 });
            check(answerRes, { [`event ${this.eventId} challenge ${this.challengeId} question ${this.questionId} correct answer accepted`]: (r) => r.json('data.is_correct') === true });
        } else {
            const answerRes = this.post(`/ng/events/${this.eventId}/challenges/${this.challengeId}/questions/${this.questionId}/submit`, {
                submission: 'wrong_flag'
            });
            check(answerRes, { [`event ${this.eventId} challenge ${this.challengeId} question ${this.questionId} incorrect answer status equals 201`]: (r) => r.status === 201 });
            check(answerRes, { [`event ${this.eventId} challenge ${this.challengeId} question ${this.questionId} incorrect answer rejected`]: (r) => r.json('data.is_correct') === false });
        }
    }

    reset_basic_challenge() {
        const resetRes = this.post(`/ng/events/${this.eventId}/challenge/${this.challengeId}/containers/recycle`, {});
        check(resetRes, { [`event ${this.eventId} challenge ${this.challengeId} reset status equals 200`]: (r) => r.status === 200 });
        check(resetRes, { [`event ${this.eventId} challenge ${this.challengeId} reset success`]: (r) => r.json('success') === true });
        check(resetRes, { [`event ${this.eventId} challenge ${this.challengeId} reset new container id`]: (r) => r.json('data') === true });
    }

    execute() {
        this.login();
        this.select_sponsor();
        this.dashboard();
        this.register_event();
        this.start_event();
        this.start_basic_challenge();
        for (let i = 0; i < 10; i++) {
            this.reset_basic_challenge();
            sleep(1);
        }

        // await this.answer_basic_challenge(false);
        // sleep(1);
        // await this.answer_basic_challenge(true);
        // sleep(1);
    }
}
