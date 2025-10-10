import useSWR, { mutate } from 'swr';
import { apiMutation } from '@/fetchers';
import type { Announcement } from '@/types';
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