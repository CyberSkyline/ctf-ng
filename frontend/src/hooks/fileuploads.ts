import { fileApiMutation } from '@/fetchers';
import type { UploadedFile } from '@/types';
import useSWR, { mutate } from 'swr';

/*
  Gets the presigned url for the file based on folder and filename.
  Filename should include the extension (png, jpeg, etc...)
*/
export function useFileUrl(folder: string, filename?: string){
  return useSWR<UploadedFile>(filename && filename !== '' ? `/fileuploads/file?folder=${folder}&filename=${filename}` : null);
}

/*
  Gets a list of all files in a specific folder
*/
export function useFileList(folder: string){
  return useSWR<UploadedFile[]>(`/fileuploads/list?folder=${folder}`)
}

/*
  Uploads a file (as FormData type) to the folder specified
  FormData: { folder, file }
*/
export function directUpload(formData: FormData){
  return fileApiMutation(`/fileuploads/upload/direct`, formData, {
    method : 'POST',
  }).then(
    (data): UploadedFile => data
  ).finally(() => {
    // Refetch the list of files in the specified folder
    mutate(`/fileuploads/list?folder=${formData.get('folder')}`)
  });
}
