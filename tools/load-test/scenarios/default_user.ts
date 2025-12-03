import { UserBrowserSession, UserHttpSession } from "../user";

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
export async function defaultUserScenario(user_session: UserHttpSession | UserBrowserSession) {
    await user_session.login();
    await user_session.close();
}