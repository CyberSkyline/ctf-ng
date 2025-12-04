import { apiMutation } from '@/fetchers';
import type { User } from '@/types';
import useSWR, { mutate } from 'swr';

/*
  Gets users with Admin or Support roles
*/
export function useSupportRoles() {
  return useSWR<User[], Error>(
    '/admin/permissions/support_role_users',
  );
}

export function useMyGlobalPermissions() {
  return useSWR<{user_id: number, permissions: string[]}, Error>(
    '/permissions/me',
  );
}

export function useMyEventPermissions(eventId: number | null) {
  return useSWR<{event_id: number, permissions: string[]}, Error>(
    eventId ? `/permissions/${eventId}/me` : null,
  );
}

export function useGlobalPermission(permission: string) {
  const { data, error, isLoading } = useMyGlobalPermissions();

  return {
    granted : data ? data.permissions.includes(permission) : false,
    denied : data ? !data.permissions.includes(permission) : false,
    isLoading,
    error,
  };
}

/**
 * Helper for performing an event-level permission check.
 */
export function useEventPermission(permission: string, eventId : number | null) {
  const { data, error, isLoading } = useMyEventPermissions(eventId);

  return {
    granted : data ? data.permissions.includes(permission) : false,
    denied : data ? !data.permissions.includes(permission) : false,
    isLoading,
    error,
  };
}

// Admin endpoints:
export function adminUpdateUserRoles(userId: number, roles: string[]) {
  return apiMutation(`/admin/permissions/${userId}/roles`, { roles }, {
    method : 'PUT',
  }).then(() => {
    mutate('/admin/users');
    mutate(`/admin/users/${userId}`);
  });
}
