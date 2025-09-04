import type { Team, TeamMember } from '@/types';
import useSWR from 'swr';

/* ADMIN ENDPOINTS */

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
