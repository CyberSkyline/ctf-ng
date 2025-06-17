import useSWR from 'swr';
import type { Event } from '../types';

/**
 * Retrieves a list of all events.
 */
export function useEvents() {
  return useSWR<{events: Event[], total_events: number}, Error>('/events');
}

/**
 * Retrieves a specific event by its ID.
 * @param eventId The ID of the event to fetch
 */
export function useEvent(eventId: string) {
  return useSWR<{event: Event}, Error>(`/events/${eventId}`);
}
