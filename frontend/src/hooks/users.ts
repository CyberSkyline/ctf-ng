import type { User } from '@/types';
import useSWR from 'swr';

export function useUsers() {
  return useSWR<{ users: Array<User>, total: number }, Error>(
    '/users/all',
  );
}

export function useUser(userId: number | null) {
  return useSWR<{ user: User }, Error>(
    userId ? `/users/${userId}` : null,
  );
}
