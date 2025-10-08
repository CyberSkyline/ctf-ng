import useSWR, { mutate } from 'swr';
import { apiMutation } from '@/fetchers';
import type { Announcement, Notification } from '@/types';

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

/**
 * Gets all announcements
 */
export function useMyAnnouncements() {
  return useSWR<Announcement[], Error>('/notifications/announcements');
}

/* ADMIN ENDPOINTS */

export function useAnnouncements() {
  return useSWR<Announcement[]>('/admin/notifications/announcements');
}

export function addNewAnnouncement(data: {title: string, message: string}) {
  return apiMutation('/admin/notifications/announce', data, {
    method : 'POST',
  }).then(() => {
    mutate('/notifications/me');
    mutate('/admin/notifications/announcements');
  });
}

export function addNewEventAnnouncement(data: { eventId: number, }) {
  return apiMutation(`/admin/notifications/events/${data.eventId}/announce`, data, {
    method : 'POST',
  }).then(() => {
    mutate('/notifications/me');
    mutate('/admin/notifications/announcements');
  });
}
