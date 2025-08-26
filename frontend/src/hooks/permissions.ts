import type { User } from '@/types';
import useSWR from 'swr';

/*
  Gets users with Admin or Support roles
*/
export function useSupportRoles() {
  return useSWR<User[], Error>(
     `/admin/permissions/support_role_users`
  );
}