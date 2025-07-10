import type { Team, TeamMember } from '@/types';
import useSWR from 'swr';

/**
 * Get a list of all teams across the system.
 * This is an admin-only endpoint.
 */
export function useAllTeams() {
  return useSWR<Team[], Error>(
    '/admin/teams',
  );
}

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
 * Get a list of teams the currently signed in user is part of.
 */
export function useMyTeams() {
  return useSWR<Team[], Error>(
    '/users/me/teams',
  );
}

/**
 * Get information about a specific team by ID.
 * This is an admin-only endpoint.
 * @param teamId The ID of the team to fetch, or null if this should not be fetched.
 */
export function useTeam(teamId: number | null) {
  return useSWR<Team, Error>(
    teamId ? `/admin/teams/${teamId}` : null,
  );
}

/**
 * Get a list of members for a specific team.
 * This is an admin-only endpoint.
 * @param teamId The ID of the team to fetch members for, or null if this should not be fetched.
 */
export function useTeamMembers(teamId: number | null) {
  return useSWR<TeamMember[], Error>(
    teamId ? `/admin/teams/${teamId}/members` : null,
  );
}
