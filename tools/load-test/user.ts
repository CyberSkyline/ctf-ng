
import { check } from 'k6';
import { Browser, Page } from 'k6/browser';
import http from 'k6/http';

export type User = {
    email: string;
    password: string;
    role: "admin" | "default";
    base_url: string;
}

export function make_user(id: number, base_url: string, role: "admin" | "default" = "default"): User {
    return {
        email: `loadtesting${id}${role === "admin" ? "admin" : ""}@example.com`,
        password: `loadtesting${id}${role === "admin" ? "admin" : ""}`,
        role: role,
        base_url: base_url
    };
}

export async function make_browser_session(user: User, browser: Browser): Promise<UserBrowserSession> {
    const page = await browser.newPage();
    return new UserBrowserSession(user, page);
}

export function make_http_session(user: User): UserHttpSession {
    return new UserHttpSession(user);
}

export class UserHttpSession {
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
        return http.post(this.url(path), body, this.params);
    }

    get(path: string) {
        return http.get(this.url(path), this.params);
    }

    async login() {
        const loginRes = this.post('/ng/users/login', {
            username: this.user.email,
            password: this.user.password,
        });

        check(loginRes, { "status equals 200": (r) => r.status === 200 });
        check(loginRes, { "login success": (r) => r.json('success') === true });
        check(loginRes, { "has session cookie": (r) => r.cookies.session.length > 0 });
    }

    async close() {
        // no-op for HTTP session
    }
}

export class UserBrowserSession {
    user: User;
    page: Page;

    constructor(user: User, page: Page) {
        this.user = user;
        this.page = page;
        throw new Error("Browser-based load testing is not yet implemented.");
    }

    url(path: string): string {
        return `${this.user.base_url}${path}`;
    }

    async login() {
        // navigate to login page
        await this.page.goto(this.url('/'));

        const loginButton = this.page.locator('button', { hasText: 'Log In' });
        await loginButton.click();

        const loginLink = this.page.locator('a', { hasText: 'Log In' });
        await loginLink.click();
        await this.page.waitForNavigation();

        const expoAccountLink = this.page.locator('a', { hasText: 'use an expo account' });
        await expoAccountLink.click();
        await this.page.waitForNavigation();

        // login
        const usernameInput = this.page.locator('input[name="username"]');
        await usernameInput.fill(this.user.email);
        const passwordInput = this.page.locator('input[name="password"]');
        await passwordInput.fill(this.user.password);
        const submitButton = this.page.locator('button[type="submit"]');
        await submitButton.click();
        await this.page.waitForNavigation()
    }

    async close() {
        await this.page.close();
    }
}

// Login


