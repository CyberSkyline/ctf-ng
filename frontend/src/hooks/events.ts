import useSWR, { mutate } from 'swr';
import { apiMutation } from '@/fetchers';
import type { Event } from '../types';

/**
 * Retrieves a list of all public and registerable events.
 */
export function useEvents() {
  return useSWR<Event[], Error>('/events');
}

/**
 * Retrieves a list of *all* events.
 * This is an admin-only endpoint.
 */
export function useAllEvents() {
  return useSWR<Event[], Error>('/admin/events');
}

/**
 * Retrieves a specific event by its ID.
 * @param eventId The ID of the event to fetch
 */
export function useEvent(eventId: number | null) {
  return useSWR<Event, Error>(eventId ? `/events/${eventId}` : null);
}

/**
 * Retrieves a specific event by its ID for admin purposes.
 * This is an admin-only endpoint.
 * @param eventId The ID of the event to fetch
 */
export function useAdminEvent(eventId: number | null) {
  return useSWR<Event, Error>(eventId ? `/admin/events/${eventId}` : null);
}

/**
 * Gets the events a user is registered for.
 * This is an admin-only endpoint.
 * @param userId The ID of the user to fetch events for, or null if this should not be fetched.
 * @returns
 */
export function useUserEvents(userId: number | null) {
  return useSWR<Event[], Error>(
    userId ? `/admin/users/${userId}/events` : null,
  );
}

/**
 * Gets the events the currently signed in user is registered for.
 */
export function useMyEvents() {
  return useSWR<Event[], Error>(
    '/users/me/events',
  );
}

/**
 * Creates a new event.
 * @param event The event object to create
 */
export function createEvent(event: Omit<Event, 'id'>) {
  apiMutation('/admin/events', event, {
    method : 'POST',
  }).then(() => {
    mutate('/admin/events');
  });
}

/**
 * Updates an existing event.
 * @param eventId ID of the event to update
 * @param updates New event data to apply
 */
export function updateEvent(eventId: number, updated: Omit<Event, 'id'>) {
  return apiMutation(`/admin/events/${eventId}`, updated, {
    method : 'PUT',
  }).then(() => {
    mutate(`/admin/events/${eventId}`);
    mutate('/admin/events');
  });
}
