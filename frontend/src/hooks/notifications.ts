import useSWR, { mutate } from 'swr';
import { apiMutation } from '@/fetchers';
import type { Notification } from '@/types';

/**
 * Retrieves a list of notifications for the logged in user
 */
export function useMyNotifications() {
  return useSWR<Notification[], Error>('/notifications/me');
}

/*
  Get a count of the unread notifications
*/
export function useUnreadCount() {
  return useSWR<{count: number}, Error>('/notifications/me/unread-count');
}

/**
 * Set a single notification as read
 */
export function markNotificationRead(id: number) {
  return apiMutation(`/notifications/me/${id}/read`, { }, {
    method : 'POST',
  }).then(() => {
    mutate('/notifications/me');
    mutate('/notifications/me/unread-count');
  });
}

/*
 * Set ALL notifications as read
*/
export function markAllNotificationsRead() {
  return apiMutation('/notifications/me/read-all', { }, {
    method : 'POST',
  }).then(() => {
    mutate('/notifications/me');
    mutate('/notifications/me/unread-count');
  });
}
