
import { Browser, Page } from 'k6/browser';

export type User = {
    email: string;
    password: string;
    role: "admin" | "default";
}

export function make_user(id: number, role: "admin" | "default" = "default"): User {
    return {
        email: `loadtesting${id}${role === "admin" ? "admin" : ""}@example.com`,
        password: `loadtesting${id}${role === "admin" ? "admin" : ""}`,
        role: role
    };
}

export async function make_session(user: User, browser: Browser): Promise<UserSession> {
    const page = await browser.newPage();
    return new UserSession(user, page);
}


export class UserSession {
    user: User;
    page: Page;

    constructor(user: User, page: Page) {
        this.user = user;
        this.page = page;
    }

    async login() {
        // navigate to login page
        await this.page.goto('http://localhost');

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


