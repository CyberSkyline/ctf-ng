export abstract class UserSession {
    abstract login(): Promise<void>;
    abstract close(): Promise<void>;
}