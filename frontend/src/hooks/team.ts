import type { Team, TeamMember } from '@/types';
import useSWR from 'swr';

export function useTeams() {
  return useSWR<{
    teams: Team[],
    total_teams: number
  }, Error>(
    '/teams/all',
  );
}

export function useEventTeams(eventId: number | null) {
  return useSWR<{
    teams: Team[],
    total_teams: number,
    event_name: string
  }, Error>(
    eventId ? `/events/${eventId}/teams` : null,
  );
}

export function useUserTeams(userId: number | null) {
  return useSWR<{
    teams: Team[]
  }, Error>(
    userId ? `/users/${userId}/teams` : null,
  );
}

export function useTeam(teamId: number | null) {
  return useSWR<{
    team: Team,
    team_members: TeamMember[]
  }, Error>(
    teamId ? `/teams/${teamId}` : null,
  );
}
