import http from 'k6/http';
import { check } from 'k6';
import { User } from '../model/user.ts';
import { UserSession } from '../session/user_session.ts';

export class UserHttpSession extends UserSession {
    user: User;
    params: http.Params;

    constructor(user: User) {
        super();
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
        return http.post(this.url(path), JSON.stringify(body), this.params);
    }

    get(path: string) {
        return http.get(this.url(path), this.params);
    }

    async login() {
        // console.log(`Logging in user ${this.user.email} with password ${this.user.password}`);
        const basePageRes = this.get('/');

        check(basePageRes, { "base page status equals 200": (r) => r.status === 200 });
        check(basePageRes, { "has session cookie": (r) => r.cookies.session.length > 0 });
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
        this.params.headers!['Content-Type'] = 'application/json';
        console.log(`Extracted CSRF Token: ${this.params.headers!['CSRF-Token']}`);
        
        const loginRes = this.post('/ng/users/login', {
            username: this.user.email,
            password: this.user.password,
        });

        check(loginRes, { "login status equals 200": (r) => r.status === 200 });
        check(loginRes, { "login success": (r) => r.json('success') === true });
        console.log(`Login response: ${loginRes.body}`);
    }

    async close() {
        // no-op for HTTP session
    }

    static make(user: User): UserHttpSession {
        return new UserHttpSession(user);
    }
}