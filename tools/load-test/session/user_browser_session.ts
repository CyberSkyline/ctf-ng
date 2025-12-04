import { Browser, Page } from "k6/browser";
import { User } from "../model/user.ts";
import { UserSession } from "../session/user_session.ts";

export class UserBrowserSession extends UserSession {
    user: User;
    page: Page;

    constructor(user: User, page: Page) {
        super();
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

    static async make(user: User, browser: Browser): Promise<UserBrowserSession> {
        const page = await browser.newPage();
        return new UserBrowserSession(user, page);
    }
}