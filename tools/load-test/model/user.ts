import { Browser, Page } from 'k6/browser';

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


// Login


