import type { Event, Team, User } from '@/types';
import useSWR from 'swr';

/**
 * Get the currently signed in user.
 */
export function useCurrentUser() {
  return useSWR<User>('/users/me');
}

/**
 * Get a list of teams the currently signed in user is part of.
 */
export function useMyTeams() {
  return useSWR<Team[], Error>(
    '/users/me/teams',
  );
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
  return useSWR<User[], Error>(
    '/admin/users',
  );
}

/**
 * Get information about a specific user.
 * This is an admin-only endpoint.
 * @param userId The ID of the user to fetch, or null if this should not be fetched.
 */
export function useUser(userId: number | null) {
  return useSWR<User, Error>(
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
