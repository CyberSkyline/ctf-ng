import { apiMutation } from '@/fetchers';
import type {
  Attempt,
  HintRedemption,
  ManualPointAward,
  Score,
  ScoreEvent,
} from '@/types';
import useSWR, { mutate } from 'swr';

export function useMyTeamScore(eventId: number | null) {
  return useSWR<Score, Error>(
    eventId ? `/scoring/${eventId}/me/team/score` : null,
  );
}

/* ADMIN ENDPOINTS */
export function useTeamScoreHistory(teamId: number | null) {
  return useSWR<{score_events: ScoreEvent[]}, Error>(
    (teamId) ? `/admin/scoring/teams/${teamId}/history` : null,
  );
}

export function useTeamAttempts(teamId: number | null) {
  return useSWR<Attempt[], Error>(
    (teamId) ? `/admin/scoring/teams/${teamId}/attempts` : null,
  );
}

export function useTeamHintRedemptions(teamId: number | null) {
  return useSWR<HintRedemption[], Error>(
    (teamId) ? `/admin/scoring/teams/${teamId}/hint_redemptions` : null,
  );
}

export function useTeamManualAwards(teamId: number | null) {
  return useSWR<ManualPointAward[], Error>(
    (teamId) ? `/admin/scoring/teams/${teamId}/manual_awards` : null,
  );
}

export function adjustPoints(teamId: number, points: number, reason: string) {
  return apiMutation(`/admin/scoring/teams/${teamId}/award-points`, { points, reason }, {
    method : 'POST',
  }).then(() => {
    mutate(`/admin/scoring/teams/${teamId}/history`);
    mutate(`/admin/scoring/teams/${teamId}/manual_awards`);
  });
}
