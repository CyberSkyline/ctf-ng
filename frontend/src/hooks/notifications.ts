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
  return useSWR<Announcement[], Error>('/announcements');
}

/* ADMIN ENDPOINTS */

export function useAnnouncements() {
  return useSWR<Announcement[]>('/admin/announcements');
}

export function addNewAnnouncement(data: {title: string, message: string}) {
  return apiMutation('/admin/announcements/announce', data, {
    method : 'POST',
  }).then(() => {
    mutate('/admin/announcements');
  });
}

export function addNewEventAnnouncement(data: {
  event_id: string,
  title: string,
  message: string,
  send_notification: boolean,
  expires_at?: Date,
  type?: string
}) {
  return apiMutation(`/admin/announcements/events/${data.event_id}/announce`, data, {
    method : 'POST',
  }).then(() => {
    mutate('/admin/announcements');
  });
}
