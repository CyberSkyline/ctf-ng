import { apiMutation } from '@/fetchers';
import type { Feedback } from '@/types';
import useSWR, { mutate } from 'swr';

export function useMyChallengeFeedback(eventId: number, challengeId: number) {
  return useSWR<Feedback | null>(
    eventId && challengeId ? `/events/${eventId}/challenges/${challengeId}/feedback` : null,
  );
}

export function submitFeedback(eventId: number, challengeId: number, feedback: Record<string, unknown>) {
  return apiMutation(
    `/events/${eventId}/challenges/${challengeId}/feedback`,
    { feedback_data : feedback },
    {
      method : 'POST',
    },
  ).then(() => {
    mutate(`/events/${eventId}/challenges/${challengeId}/feedback`);
  });
}

// ADMIN ROUTES

export function useChallengeFeedback(eventId: number, challengeId: number) {
  return useSWR<Feedback[]>(
    eventId && challengeId ? `/admin/events/${eventId}/challenges/${challengeId}/feedback` : null,
  );
}
