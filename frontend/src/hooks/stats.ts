import useSWR from 'swr';

// eslint-disable-next-line import/prefer-default-export
export function useCounts() {
  return useSWR<{ users: number; events: number; teams: number; }>('/admin/stats/counts');
}
