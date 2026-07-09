import useSWR, { mutate } from 'swr';
import { apiMutation } from '@/fetchers';
import type { Notification } from '@/types';
import { useEffect, useState } from 'react';

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
 * Manages the local storage and state of the notification sound setting
 */
const STORAGE_KEY = 'notificationSound';

export function useNotificationSound() {
  const [ enabled, setEnabled ] = useState(() => localStorage.getItem(STORAGE_KEY) !== 'false');

  useEffect(() => {
    const handleStorageChange = () => {
      setEnabled(localStorage.getItem(STORAGE_KEY) !== 'false');
    };

    // storage - event is fired when localStorage is changed in another tab, but not in the same tab.
    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('notificationSoundChange', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('notificationSoundChange', handleStorageChange);
    };
  }, []);

  const setNotificationSound = (value: boolean) => {
    localStorage.setItem(STORAGE_KEY, String(value));
    setEnabled(value);

    // Needed because storage event does not fire in the same tab that made the change
    window.dispatchEvent(new Event('notificationSoundChange'));
  };

  return [ enabled, setNotificationSound ] as const;
}
