import { apiMutation } from '@/fetchers';
import type { Team, TeamMember } from '@/types';
import useSWR, { mutate } from 'swr';

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

export function adminUpdateTeam(teamId: number, updatedTeam: Pick<Team, 'name' | 'ranked' | 'start_timestamp' | 'end_time'>) {
  return apiMutation(`/admin/teams/${teamId}`, updatedTeam, {
    method : 'PUT',
  }).then(() => {
    mutate(`/admin/teams/${teamId}`);
    mutate('/admin/teams');
  });
}

/**
 * Promote a user to captain
 * @param teamId The ID of the team
 * @param userId The ID of the user to promote
 */
export function adminPromoteTeamMember(teamId: number, userId: number) {
  return apiMutation(`/admin/teams/${teamId}/promote`, { user_id : userId }, {
    method : 'POST',
  }).then(() => {
    mutate(`/admin/teams/${teamId}/members`);
  });
}

/**
 * Kick a user from a team
 */
export function adminKickTeamMember(teamId: number, userId: number) {
  return apiMutation(`/admin/teams/${teamId}/kick`, { user_id : userId }, {
    method : 'POST',
  }).then(() => {
    // member count value has changed, so refresh team as well as members list
    mutate('/admin/teams');
    mutate(`/admin/teams/${teamId}`);

    mutate(`/admin/teams/${teamId}/members`);
  });
}
