import { apiMutation } from '@/fetchers';
import type {
  Attempt,
  Challenge,
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

export function createChallenge(eventId: number, yaml: string) {
  return apiMutation(`/admin/events/${eventId}/challenges`, { yaml : btoa(yaml) }, {
    method : 'POST',
  }).then(() => {
    // refresh the challenges list when a new challenge is created
    mutate(`/events/${eventId}/challenges`);
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
