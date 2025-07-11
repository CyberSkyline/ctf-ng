import type { User } from '@/types';
import useSWR from 'swr';

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
 * Get the currently signed in user.
 */
export function useCurrentUser() {
  return useSWR<User>('/users/me');
}
