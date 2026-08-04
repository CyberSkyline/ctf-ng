import useSWR from 'swr';

/* ADMIN ENDPOINTS */

/*
  Gets a list of available certificate templates
*/
// eslint-disable-next-line import/prefer-default-export
export function useCertificateTemplates() {
  return useSWR<{files: string[]}>('/admin/certificates');
}
