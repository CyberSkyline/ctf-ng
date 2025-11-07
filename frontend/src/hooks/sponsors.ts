import { apiMutation } from '@/fetchers';
import type { Sponsor } from '@/types';
import useSWR, { mutate } from 'swr';

export function useSponsors(){
  return useSWR<Sponsor[], Error>('/sponsors');
}

export function useSponsorById(id: number | null){
  return useSWR<Sponsor, Error>(
    id ? `/sponsors/${id}` : null
  );
}

/* ADMIN ENDPOINTS */

export function useAdminSponsors(){
  return useSWR<Sponsor[], Error>('/admin/sponsors');
}

export function useAdminSponsorById(id: number | null){
  return useSWR<Sponsor, Error>(
    id ? `/admin/sponsors/${id}` : null
  );
}

export function createSponsor(formData: {
  name: string,
  logo?: string,
}){
  return apiMutation('/admin/sponsors', formData, {
    method : 'POST',
  }).then(() => {
    mutate('/sponsors');
    mutate('/admin/sponsors');
  });
}

export function editSponsor(id : number, formData: {
  name: string,
  logo?: string,
}){
  return apiMutation(`/admin/sponsors/${id}`, formData, {
    method : 'PUT',
  }).then(() => {
    mutate('/sponsors');
    mutate('/admin/sponsors');
  });
}