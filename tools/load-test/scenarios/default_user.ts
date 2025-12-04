import { UserSession } from "../session/user_session.ts";

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
export async function defaultUserScenario(user_session: UserSession) {
    await user_session.login();
    await user_session.close();
}