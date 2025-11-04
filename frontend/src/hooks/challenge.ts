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

export function useChallenge(eventId: number | null, challengeId: number | null) {
  return useSWR<{
    challenge: Challenge;
    questions: Question[];
    hints: Hint[];
    attempts: Attempt[];
  }, Error>(
    eventId && challengeId ? `/events/${eventId}/challenges/${challengeId}` : null,
  );
}

export function submitAnswer(
  eventId: number,
  challengeId: number,
  questionId: number,
  answer: string,
) {
  return apiMutation(`/events/${eventId}/challenges/${challengeId}/submit`, {
    question_id : questionId,
    submission : answer,
  }, {
    method : 'POST',
  }).then(() => {
    // refresh the attempts list when submission goes through
    mutate(`/events/${eventId}/challenges/${challengeId}`);
  });
}

export function redeemHint(
  eventId: number,
  challengeId: number,
  hintId: number,
) {
  return apiMutation(`/events/${eventId}/challenges/${challengeId}/hint/${hintId}/redeem`, undefined, {
    method : 'POST',
  }).then(() => {
    // refresh the hints list when hint is redeemed
    mutate(`/events/${eventId}/challenges/${challengeId}`);
  });
}

export function submitFlag(
  eventId: number,
  challengeId: number,
  questionId: number,
  flag: string,
) {
  return apiMutation(`/events/${eventId}/challenges/${challengeId}/questions/${questionId}/submit`, {
    submission : flag,
  }, {
    method : 'POST',
  }).then(() => {
    // refresh the challenge data after submitting a flag
    mutate(`/events/${eventId}/challenges/${challengeId}`);
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

export function useAdminChallengeYaml(challengeId: number | null) {
  return useSWR<{ yaml: string }, Error>(
    challengeId ? `/admin/challenges/${challengeId}/yaml` : null,
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
  return apiMutation('/admin/challenges', { yaml : btoa(yaml), event_id : eventId }, {
    method : 'POST',
  }).then(() => {
    // refresh the challenges list when a new challenge is created
    mutate(`/admin/events/${eventId}/challenges`);
  });
}

export function updateChallenge(challengeId: number, yaml: string) {
  return apiMutation(`/admin/challenges/${challengeId}`, { yaml : btoa(yaml) }, {
    method : 'PUT',
  }).then(() => {
    // refresh the challenges list when a challenge is updated
    mutate('/admin/challenges');
    mutate(`/admin/challenges/${challengeId}/yaml`);
    mutate(`/admin/challenges/${challengeId}/questions`);
    mutate(`/admin/challenges/${challengeId}/hints`);
    mutate(`/admin/challenges/${challengeId}/blueprints`);
  });
}
