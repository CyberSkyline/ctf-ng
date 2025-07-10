import useSWR, { mutate } from 'swr';
import { apiMutation } from '@/fetchers';
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
export function useEvent(eventId: number | null) {
  return useSWR<{event: Event}, Error>(eventId ? `/events/${eventId}` : null);
}

/**
 * Creates a new event.
 * @param event The event object to create
 */
export function createEvent(event: Omit<Event, 'id'>) {
  apiMutation('/events', event, {
    method : 'POST',
  }).then(() => {
    mutate('/events');
  });
}

/**
 * Updates an existing event.
 * @param eventId ID of the event to update
 * @param updates Patches to apply to the event data
 */
export function updateEvent(eventId: number, updates: Partial<Omit<Event, 'id'>>) {
  apiMutation(`/events/${eventId}`, updates, {
    method : 'PATCH',
  }).then(() => {
    mutate(`/events/${eventId}`);
    mutate('/events');
  });
}
