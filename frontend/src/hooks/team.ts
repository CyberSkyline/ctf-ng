import { apiMutation } from '@/fetchers';
import type {
  Attempt,
  HintRedemption,
  ManualPointAward,
  Score,
  ScoreEvent,
  Team,
  TeamMember,
} from '@/types';
import useSWR, { mutate } from 'swr';

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

export function useMyTeamScore(eventId: number | null) {
  return useSWR<Score, Error>(
    eventId ? `/events/${eventId}/me/team/score` : null,
  );
}

export function useTeamScoreHistory(eventId: number| null, teamId: number | null) {
  return useSWR<{score_events: ScoreEvent[]}, Error>(
    (eventId && teamId) ? `/admin/scoring/events/${eventId}/teams/${teamId}/history` : null,
  );
}

export function useTeamAttempts(eventId: number | null, teamId: number | null) {
  return useSWR<Attempt[], Error>(
    (eventId && teamId) ? `/admin/scoring/events/${eventId}/teams/${teamId}/attempts` : null,
  );
}

export function useTeamHintRedemptions(eventId: number | null, teamId: number | null) {
  return useSWR<HintRedemption[], Error>(
    (eventId && teamId) ? `/admin/scoring/events/${eventId}/teams/${teamId}/hint_redemptions` : null,
  );
}

export function useTeamManualAwards(eventId: number | null, teamId: number | null) {
  return useSWR<ManualPointAward[], Error>(
    (eventId && teamId) ? `/admin/scoring/events/${eventId}/teams/${teamId}/manual_awards` : null,
  );
}

export function adjustPoints(eventId: number, teamId: number, points: number, reason: string) {
  return apiMutation(`/admin/scoring/events/${eventId}/teams/${teamId}/award-points`, { points, reason }, {
    method : 'POST',
  }).then(() => {
    mutate(`/admin/scoring/events/${eventId}/teams/${teamId}/history`);
    mutate(`/admin/scoring/events/${eventId}/teams/${teamId}/manual_awards`);
  });
}
