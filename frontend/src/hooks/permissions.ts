import type { User } from '@/types';
import useSWR from 'swr';

/*
  Gets users with Admin or Support roles
*/

/* eslint-disable import/prefer-default-export */
// ^ remove disable line after implementing more permission checks
export function useSupportRoles() {
  return useSWR<User[], Error>(
    '/admin/permissions/support_role_users',
  );
}
