import { ROUTEPREFIX } from '@/constants';
import { apiMutation } from '@/fetchers';
import { useMyEvents } from '@/hooks/events';
import type {
  AdminUser,
  Event,
  Team,
  User,
  Workspace,
} from '@/types';
import { keyBy } from 'lodash';
import useSWR, { mutate } from 'swr';

/**
 * Get the currently signed in user.
 */
export function useCurrentUser() {
  return useSWR<User, Error>('/users/me', {
    shouldRetryOnError(err) {
      // Don't retry if we get a 401 (not logged in)
      return !err.message.includes('Authentication is required');
    },
  });
}

/**
 * Helper for checking auth state. Uses window.init to determine if authed on page load,
 * then switches to useCurrentUser once it loads to allow for reactive updates.
 *
 * Once the current user is loaded, the user object (if authenticated) will also be returned for convenience.
 */
export function useAuth() {
  const { data, error, isLoading } = useCurrentUser();

  if (isLoading) {
    // hook has not responded yet, fall back to window.init value
    return {
      user : undefined,
      isAuthenticated : !!window.init.userId,
      isUnauthenticated : window.init.userId === null,
      isLoading,
      isImpersonated : window.init.impersonated,
    };
  }

  return {
    user : data,
    isAuthenticated : !!data,
    isUnauthenticated : !data && error?.message.includes('Authentication is required'),
    isLoading,
    isImpersonated : window.init.impersonated,
  };
}

/**
 * Helper for checking if the user is registered for a specific event.
 * @param eventId The ID of the event to check registration for.
 */
export function useRegistration(eventId: number | null) {
  const { isUnauthenticated } = useAuth();
  const { data, error, isLoading } = useSWR<Team[], Error>(
    !isUnauthenticated && !!eventId && '/users/me/teams',
  );

  const myTeam = data?.find((team) => team.event_id === eventId);

  return {
    isRegistered : !!myTeam,
    isUnregistered : !myTeam && !isLoading && !error,
    isStarted : !!myTeam?.start_timestamp,
    isFinished : !!(myTeam?.end_time && myTeam.end_time < new Date()),
    team : myTeam,
    error,
    isLoading,
  };
}

/**
 * Get a list of teams the currently signed in user is part of.
 */
export function useMyTeams() {
  return useSWR<Team[], Error>(
    '/users/me/teams',
  );
}

/**
 * Gets the most recent team/leaderboard name the user has been associated with.
 * @param isTeamGame Whether to look for the last team event name (true) or individual event leaderboard name (false).
 */
export function usePreviousName(isTeamGame: boolean) {
  // get both teams and events here to allow filtering by event properties
  const { data : myTeams = [], isLoading : teamsLoading } = useMyTeams();
  const { data : myEvents = [], isLoading : eventsLoading } = useMyEvents();

  const eventsById = keyBy(myEvents, 'id');
  const filteredTeams = myTeams
    .filter((team) => {
      const event = eventsById[team.event_id];

      // we don't want to populate auto-generated names into the registration form, only past user-provided ones.
      // also don't fill past team names for individual events and vice versa.
      return !!event && !event.practice && (isTeamGame ? event.max_team_size > 1 : event.max_team_size === 1);
    });

  // last item in the list is the most recent team join, get the name associated with that or null if not present.
  return { data : filteredTeams.at(-1)?.name || null, isLoading : teamsLoading || eventsLoading };
}

/* Get the user's sponsor/affiliation */
export function useMySponsor() {
  return useSWR('/users/me/sponsor');
}

/* Set the user's sponsor/affiliation */
export function setMySponsor(id: number) {
  return apiMutation('/users/me/sponsor', { sponsor_id : id }, {
    method : 'PUT',
  }).then(() => {
    mutate('/users/me/sponsor');
  });
}

/* ADMIN ENDPOINTS */

/**
 * Get a list of teams the given user is part of.
 * This is an admin-only endpoint.
 * @param userId The ID of the user to fetch teams for, or null if this should not be fetched.
 */
export function useUserTeams(userId: number | null) {
  return useSWR<Team[], Error>(
    userId ? `/admin/users/${userId}/teams` : null,
  );
}

/**
 * Get a list of all users.
 * This is an admin-only endpoint.
 */
export function useAllUsers() {
  return useSWR<AdminUser[], Error>(
    '/admin/users',
  );
}

/**
 * Get information about a specific user.
 * This is an admin-only endpoint.
 * @param userId The ID of the user to fetch, or null if this should not be fetched.
 */
export function useUser(userId: number | null) {
  return useSWR<AdminUser, Error>(
    userId ? `/admin/users/${userId}` : null,
  );
}

/**
 * Admin Only endpoint
 * Get events for a specific user
 */
export function useUserEvents(userId: number | undefined) {
  return useSWR<Event[], Error>(
    userId ? `/admin/users/${userId}/events` : null,
  );
}

export function useUserWorkspace(userId: number) {
  return useSWR<Workspace, Error>(`/admin/users/${userId}/container`);
}

export function useWorkspaceStatus(userId : number) {
  return useSWR<string, Error>(`/admin/users/${userId}/container/status`, {
    refreshInterval : 5000, // Refresh every 5 seconds
  });
}

export function createUser(user: Pick<User, 'name' | 'email'> & { password: string }) {
  return apiMutation('/admin/users', user, {
    method : 'POST',
  }).then((data) => {
    mutate('/admin/users');
    return data as AdminUser;
  });
}

export function adminUpdateUser(userId: number, user: Pick<User, 'name' | 'email'>) {
  return apiMutation(`/admin/users/${userId}`, user, {
    method : 'PUT',
  }).then(() => {
    mutate(`/admin/users`);
    mutate(`/admin/users/${userId}`);
  });
}

export function restartWorkspace(userId : number) {
  return apiMutation(`/admin/users/${userId}/container/restart`, undefined, {
    method : 'POST',
  }).then(() => {
    mutate(`/admin/users/${userId}/container`);
    mutate(`/admin/users/${userId}/container/status`);
  });
}

export function recycleWorkspace(userId : number) {
  return apiMutation(`/admin/users/${userId}/container/recycle`, undefined, {
    method : 'POST',
  }).then(() => {
    mutate(`/admin/users/${userId}/container`);
    mutate(`/admin/users/${userId}/container/status`);
  });
}

export function deleteWorkspace(userId : number) {
  return apiMutation(`/admin/users/${userId}/container/delete`, undefined, {
    method : 'POST',
  }).then(() => mutate(`/admin/users/${userId}/container/status`));
}

export function impersonateUser(userId: number) {
  return apiMutation('/admin/impersonate', { user_id : userId }, {
    method : 'POST',
  }).then(() => {
    // On success, redirect to the home page to refresh the session
    window.location.href = `${ROUTEPREFIX}/`;
  });
}

export function stopImpersonation() {
  return apiMutation('/admin/stop_impersonating', {}, {
    method : 'POST',
  }).then((data: unknown) => {
    // On success, redirect to the admin user page
    window.location.href = `${ROUTEPREFIX}/admin/users?id=${data}`;
  });
}

export function banUser(userId: number) {
  return apiMutation(`/admin/users/${userId}/ban`, {}, {
    method : 'POST',
  }).then(() => {
    mutate(`/admin/users/${userId}`);
    mutate('/admin/users');
  });
}

export function unbanUser(userId: number) {
  return apiMutation(`/admin/users/${userId}/unban`, {}, {
    method : 'POST',
  }).then(() => {
    mutate(`/admin/users/${userId}`);
    mutate('/admin/users');
  });
}
