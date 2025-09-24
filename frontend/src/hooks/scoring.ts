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
    eventId ? `/events/${eventId}/me/team/score` : null,
  );
}

/* ADMIN ENDPOINTS */
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
