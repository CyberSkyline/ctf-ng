import { Browser, Page } from 'k6/browser';

export type User = {
    id: number;
    email: string;
    password: string;
    role: "admin" | "default";
    base_url: string;
}

export function make_user(id: number, email: string, password: string, base_url: string, role: "admin" | "default" = "default"): User {
    return {
        id: id,
        email: email,
        password: password,
        role: role,
        base_url: base_url
    };
}
