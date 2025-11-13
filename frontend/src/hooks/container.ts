import { apiMutation } from '@/fetchers';
import type { ContainerInstance, ContainerStatus, Deployment } from '@/types';
import useSWR, { mutate } from 'swr';

export function useCurrentChallengeId() {
  return useSWR<number | null>('/container/me/current_challenge');
}

export function connectWorkspace(challengeId: number) {
  return apiMutation(`/challenge/${challengeId}/containers`, undefined, {
    method : 'POST',
  }).then(() => {
    // refresh the current challenge ID after connecting workspace
    mutate('/container/me/current_challenge');
  });
}

export function recycleChallengeContainers(eventId: number, challengeId: number) {
  return apiMutation(`/events/${eventId}/challenge/${challengeId}/containers/recycle`, undefined, {
    method : 'POST',
  }).then(() => {
    mutate('/container/me/current_challenge');
  });
}

/* ADMIN ENDPOINTS */

export function useAllDeployments() {
  return useSWR<Deployment[], Error>('/admin/container');
}

export function useDeploymentServices(challengeId: number, teamId: number) {
  return useSWR<ContainerInstance[], Error>(`/admin/container/challenge/${challengeId}/team/${teamId}/services`);
}

export function useContainerStatus(id: number) {
  return useSWR<ContainerStatus, Error>(`/admin/container/${id}/status`, {
    refreshInterval : 5000, // Refresh every 5 seconds
  });
}

export function useContainerLogs(containerId: number) {
  return useSWR<string, Error>(`/admin/container/${containerId}/logs`, {
    dedupingInterval : 100, // Deduplicate requests for only 100ms - reopening logs should not use stale data
  });
}

export function useProvisionerStats() {
  return useSWR<{ containers_running: number; os: string; cpus: number, memory: number }, Error>(
    '/admin/container/stats',
    { refreshInterval : 30000 }, // Refresh metrics every 30 sec while they are on the page
  );
}

export function restartContainer(containerId: number) {
  return apiMutation(`/admin/container/${containerId}/restart`, undefined, {
    method : 'POST',
  }).then(() => {
    mutate(`/admin/container/${containerId}/status`);
  });
}

export function recycleContainer(containerId: number) {
  return apiMutation(`/admin/container/${containerId}/recycle`, undefined, {
    method : 'POST',
  }).then(() => {
    mutate(`/admin/container/${containerId}/status`);
  });
}
