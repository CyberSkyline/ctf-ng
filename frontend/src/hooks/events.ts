import { apiMutation } from '@/fetchers';
import type {
  Event,
  Score,
  Sponsor,
  Team,
  TeamMember,
} from '@/types';
import useSWR, { mutate } from 'swr';

/**
 * Retrieves a list of all public and registerable competition events
 */
export function useCompetitionEvents() {
  return useSWR<Event[], Error>('/events?practice=false');
}

/**
 * Retrieves a list of all public and registerable practice events
 */
export function usePracticeEvents() {
  return useSWR<Event[], Error>('/events?practice=true');
}

/**
 * Retrieves a specific event by its ID.
 * @param eventId The ID of the event to fetch
 */
export function useEvent(eventId: number | null) {
  return useSWR<Event, Error>(eventId ? `/events/${eventId}` : null);
}

export function useEventStatus(eventId: number | null) {
  const { data, error, isLoading } = useEvent(eventId);

  return {
    isRegistrationOpen : !!(data && data.registration_open
      && (!data.registration_start_date || new Date(data.registration_start_date) <= new Date())
      && (!data.registration_end_date || new Date(data.registration_end_date) >= new Date())
    ),
    isOngoing : !!(data
       && (!data.start_time || new Date(data.start_time) <= new Date())
       && (!data.end_time || new Date(data.end_time) >= new Date())),
    isConcluded : !!(data && data.end_time && new Date(data.end_time) < new Date()),
    isLoading,
    error,
    event : data,
  };
}

export function useMyEligibility(eventId: number | null) {
  return useSWR<boolean, Error>(eventId ? `/events/${eventId}/me/eligibility` : null);
}

/**
 * Registeres user for a specific event
 * @param event_id The event id
 * @param team_name The leaderboard name for solo events or team name for team creation
 * @param invite_code The invite code of the team you want to join
 */
export function registerMyEvent(eventId: number, teamName: string) {
  return apiMutation(`/events/${eventId}/me/register`, { team_name : teamName }, {
    method : 'POST',
  }).then(() => Promise.all([
    mutate('/users/me/events'),
    mutate('/users/me/teams'),
    mutate(`/events/${eventId}/me/team`),
    mutate(`/permissions/${eventId}/me`),
  ])).then(() => {
    mutate(`/events/${eventId}/me/eligibility`);
  });
}
export function registerMyEventTeamJoin(eventId: number, inviteCode: string) {
  return apiMutation(`/events/${eventId}/me/register`, { invite_code : inviteCode }, {
    method : 'POST',
  }).then(() => Promise.all([
    mutate('/users/me/events'),
    mutate('/users/me/teams'),
    mutate(`/events/${eventId}/me/team`),
    mutate(`/permissions/${eventId}/me`),
  ])).then(() => {
    mutate(`/events/${eventId}/me/eligibility`);
  });
}

/**
 * Registers user for practice event
 * @param event_id The event id
 */
export function registerMyPracticeEvent(eventId: number) {
  return apiMutation(`/events/${eventId}/me/register`, {}, {
    method : 'POST',
  }).then(() => mutate(`/permissions/${eventId}/me`).then(() => Promise.all([
    mutate('/users/me/events'),
    mutate('/users/me/teams'),
    mutate(`/events/${eventId}/me/team`),
  ])).then(() => {
    mutate(`/events/${eventId}/me/eligibility`);
  }));
}

export function useTeamNameFromCode(eventId: number, inviteCode?: string) {
  return useSWR(
    inviteCode ? `/events/${eventId}/team/${inviteCode}` : null,
  );
}

/**
 * Gets the current user's team for a specific event
 * @param eventId The id of the event, if undefined this should not fetch
 * @returns a Team object
 */
export function useMyTeam(eventId: number | undefined) {
  return useSWR<Team, Error>(
    eventId ? `/events/${eventId}/me/team` : null,
  );
}

/**
 * @param eventId The id of the event
 * @param userId The user id of the player to kick off the team
 */
export function kickFromMyTeam(eventId: number, userId: number) {
  return apiMutation(`/events/${eventId}/me/team/kick`, { user_id : userId }, {
    method : 'POST',
  }).then(() => {
    mutate(`/events/${eventId}/me/team`);
    mutate(`/events/${eventId}/me/team/members`);
  });
}

/**
 * @param eventId The id of the event
 * @param newCaptain The user id of the new captain, optional
 */
export function leaveMyTeam(eventId: number) {
  return apiMutation(`/events/${eventId}/me/team/leave`, { }, {
    method : 'POST',
  }).then(() => {
    mutate(`/events/${eventId}/me/team`);
    mutate('/users/me/teams');
    mutate('/users/me/events');
    mutate(`/events/${eventId}/me/eligibility`);
    // zero out permissions to avoid caching stale ones from previous registration
    mutate(`/permissions/${eventId}/me`, { permissions : [] });
  });
}

/**
 * @param eventId The id of the event
 * @param userId The user id of the new captain
 */
export function promoteMyCaptain(eventId: number, userId: number) {
  return apiMutation(`/events/${eventId}/me/team/promote`, { user_id : userId }, {
    method : 'POST',
  }).then(() => {
    mutate(`/events/${eventId}/me/team/members`);
    mutate(`/permissions/${eventId}/me`);
  });
}

/**
 * @param eventId The id of the event, if undefined this should not fetch
 * @returns a list of Team Members
 */
export function useMyTeamMembers(eventId: number | undefined) {
  return useSWR<TeamMember[], Error>(
    eventId ? `/events/${eventId}/me/team/members` : null,
  );
}

/**
 * Starts the user's team for a specific event. User must be captain.
 * @param eventId The id of the event
 */
export function startMyTeam(eventId: number) {
  return apiMutation(`/events/${eventId}/me/team/start`, undefined, {
    method : 'POST',
  }).then(() => {
    mutate(`/events/${eventId}/me/team`);
    mutate(`/events/${eventId}/challenges`);
    mutate(`/events/${eventId}/me/challenges`);
    mutate(`/permissions/${eventId}/me`);
    mutate('/users/me/teams');
  });
}

/**
 * @param eventId The id of the event
 * @param teamName The new name for the team
 * @returns a new team object
 */
export function updateTeamName(eventId: number, teamName: Team['name']) {
  return apiMutation(`/events/${eventId}/me/team/update_name`, { name : teamName }, {
    method : 'PUT',
  }).then(() => {
    mutate('/users/me/team');
    mutate('/users/me/teams');
    mutate(`/events/${eventId}/me/team`);
    mutate(`/events/${eventId}/leaderboard`);
  });
}

/**
 * Gets the events the currently signed in user is registered for.
 */
export function useMyEvents() {
  return useSWR<Event[], Error>(
    '/users/me/events',
  );
}

export function useLeaderboard(eventId: number) {
  return useSWR<(Score & {sponsors: Sponsor[]})[], Error>(eventId ? `/events/${eventId}/leaderboard` : null);
}

/* ADMIN ENDPOINTS */

/**
 * Retrieves a list of *all* events.
 * This is an admin-only endpoint.
 */
export function useAllEvents() {
  return useSWR<Event[], Error>('/admin/events');
}

/**
 * Retrieves a specific event by its ID for admin purposes.
 * This is an admin-only endpoint.
 * @param eventId The ID of the event to fetch
 */
export function useAdminEvent(eventId: number | null) {
  return useSWR<Event, Error>(eventId ? `/admin/events/${eventId}` : null);
}

export function adminRegisterEvent(eventId: number, userId: number, teamName: string) {
  return apiMutation(`/admin/events/${eventId}/${userId}/register`, { team_name : teamName }, {
    method : 'POST',
  }).then(() => {
    mutate(`/admin/users/${userId}/events`);
    mutate(`/admin/users/${userId}/teams`);
  });
}

export function adminRegisterEventTeamJoin(eventId: number, userId: number, inviteCode: string) {
  return apiMutation(`/admin/events/${eventId}/${userId}/register`, { invite_code : inviteCode }, {
    method : 'POST',
  }).then(() => {
    mutate(`/admin/users/${userId}/events`);
    mutate(`/admin/users/${userId}/teams`);
  });
}

/**
 * Creates a new event.
 * @param event The event object to create
 */
export function createEvent(event: { name : string }) {
  return apiMutation('/admin/events', event, {
    method : 'POST',
  })
    .then((data) => (data as Event).id)
    .finally(() => {
      mutate('/admin/events');
    });
}

/**
 * Updates an existing event.
 * @param eventId ID of the event to update
 * @param updates New event data to apply
 */
export function updateEvent(eventId: number, updated: Omit<Event, 'id'>) {
  return apiMutation(`/admin/events/${eventId}`, updated, {
    method : 'PUT',
  }).then(() => {
    mutate(`/admin/events/${eventId}`);
    mutate('/admin/events');
  });
}
