import useSWR, { mutate } from 'swr';
import { apiMutation } from '@/fetchers';
import type { Event, Team, TeamMember } from '@/types';

/**
 * Retrieves a list of all public and registerable events.
 */
export function useEvents() {
  return useSWR<Event[], Error>('/events');
}

/**
 * Retrieves a list of *all* events.
 * This is an admin-only endpoint.
 */
export function useAllEvents() {
  return useSWR<Event[], Error>('/admin/events');
}

/**
 * Retrieves a specific event by its ID.
 * @param eventId The ID of the event to fetch
 */
export function useEvent(eventId: number | null) {
  return useSWR<Event, Error>(eventId ? `/events/${eventId}` : null);
}

/**
 * Retrieves a specific event by its ID for admin purposes.
 * This is an admin-only endpoint.
 * @param eventId The ID of the event to fetch
 */
export function useAdminEvent(eventId: number | null) {
  return useSWR<Event, Error>(eventId ? `/admin/events/${eventId}` : null);
}

/**
 * Gets the events a user is registered for.
 * This is an admin-only endpoint.
 * @param userId The ID of the user to fetch events for, or null if this should not be fetched.
 * @returns
 */
export function useUserEvents(userId: number | null) {
  return useSWR<Event[], Error>(
    userId ? `/admin/users/${userId}/events` : null,
  );
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
  }).then(() => {
    mutate('/users/me/events');
  });
}
export function registerMyEventTeamJoin(eventId: number, inviteCode: string) {
  return apiMutation(`/events/${eventId}/me/register`, { invite_code : inviteCode }, {
    method : 'POST',
  }).then(() => {
    mutate('/users/me/events');
  });
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
export function leaveMyTeam(eventId: number, newCaptain: number) {
  return apiMutation(`/events/${eventId}/me/team/leave`, { captain : newCaptain }, {
    method : 'POST',
    // cj the docs are wrong. This should be a post
    // cj unless this is supposed to be 2 separate operations, this should take a captain as an optional param
  }).then(() => {
    mutate('/users/me/events');
    // cj - do I need to mutate the useMyTeam and useMyTeamMembers here?
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
 * @param eventId The id of the event
 * @param teamName The new name for the team
 * @returns a new team object
 */
export function updateTeamName(eventId: number, teamName: Team['name']) {
  return apiMutation(`/events/${eventId}/me/team/update_name`, { name : teamName }, {
    method : 'PUT',
  }).then(() => {
    mutate('/users/me/team');
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

/**
 * Creates a new event.
 * @param event The event object to create
 */
export function createEvent(event: Omit<Event, 'id'>) {
  return apiMutation('/admin/events', event, {
    method : 'POST',
  }).then(() => {
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
