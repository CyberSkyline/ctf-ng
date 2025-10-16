import { apiMutation } from '@/fetchers';
import type {
  AdminQuestion,
  Attempt,
  Challenge,
  ContainerBlueprint,
  Hint,
  MeChallenge,
  Question,
} from '@/types';
import useSWR, { mutate } from 'swr';

export function useEventChallenges(eventId: number | null) {
  return useSWR<Challenge[], Error>(
    eventId ? `/events/${eventId}/challenges` : null,
  );
}

// Get the challenge stats for the current user's team
export function useMyChallenges(eventId: number | null) {
  return useSWR<MeChallenge[], Error>(
    eventId ? `/events/${eventId}/me/challenges` : null,
  );
}

export function useChallenge(challengeId: number | null) {
  return useSWR<{
    challenge: Challenge;
    questions: Question[];
    hints: Hint[];
    attempts: Attempt[];
  }, Error>(
    challengeId ? `/events/challenges/${challengeId}` : null,
  );
}

export function redeemHint(
  challengeId: number,
  hintId: number,
) {
  return apiMutation(`/hint/${hintId}/redeem`, undefined, {
    method : 'POST',
  }).then(() => {
    // refresh the hints list when hint is redeemed
    mutate(`/events/challenges/${challengeId}`);
  });
}

export function submitFlag(
  challengeId: number,
  questionId: number,
  flag: string,
) {
  return apiMutation(`/scoring/questions/${questionId}/submit`, {
    submission : flag,
  }, {
    method : 'POST',
  }).then(() => {
    // refresh the challenge data after submitting a flag
    mutate(`/events/challenges/${challengeId}`);
  });
}

/* ADMIN ENDPOINTS */
export function useAllChallenges() {
  return useSWR<Challenge[], Error>('/admin/challenges');
}

export function useAdminEventChallenges(eventId: number | null) {
  return useSWR<Challenge[], Error>(
    eventId ? `/admin/events/${eventId}/challenges` : null,
  );
}

export function useAdminChallengeAttempts(challengeId: number | null) {
  return useSWR<Attempt[], Error>(
    challengeId ? `/admin/challenges/${challengeId}/attempts` : null,
  );
}

export function useAdminChallengeQuestions(challengeId: number | null) {
  return useSWR<AdminQuestion[], Error>(
    challengeId ? `/admin/challenges/${challengeId}/questions` : null,
  );
}

export function useAdminChallengeHints(challengeId: number | null) {
  return useSWR<Hint[], Error>(
    challengeId ? `/admin/challenges/${challengeId}/hints` : null,
  );
}

export function useAdminChallengeBlueprints(challengeId: number | null) {
  return useSWR<ContainerBlueprint[], Error>(
    challengeId ? `/admin/challenges/${challengeId}/blueprints` : null,
  );
}

export function createChallenge(eventId: number, yaml: string) {
  return apiMutation(`/admin/events/${eventId}/challenges`, { yaml : btoa(yaml) }, {
    method : 'POST',
  }).then(() => {
    // refresh the challenges list when a new challenge is created
    mutate(`/admin/events/${eventId}/challenges`);
  });
}
