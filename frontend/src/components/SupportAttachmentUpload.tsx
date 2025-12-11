import { ticketAttachmentUpload } from '@/hooks/fileuploads';
import { compressImageFile } from '@/util';
import { Spinner } from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import { useState } from 'react';
import Dropzone from 'react-dropzone';
import { twMerge } from 'tailwind-merge';

export default function SupportAttachmentUpload({ fileUploadPath, ticketMutationUrl } : { fileUploadPath : string, ticketMutationUrl : string }) {
  const [ uploadError, setUploadError ] = useState<string | null>(null);
  const [ loading, setLoading ] = useState<boolean>(false);
  const [ uploadedImageSrc, setUploadedImageSrc ] = useState<string | null>(null);

  const onDrop = async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]; // Only accepting 1 file at a time

    const compressedFile = await compressImageFile(file);

    setUploadError(null);
    setLoading(true);

    ticketAttachmentUpload(fileUploadPath, compressedFile, ticketMutationUrl)
      .then((result) => setUploadedImageSrc(result.download_url || null))
      .catch((err) => setUploadError(err.message))
      .finally(() => setLoading(false));
  };

  if (uploadedImageSrc) {
    return null; // Hide after a successful upload
    // return (
    //   <Box maxHeight="256px" maxWidth="256px">
    //     <img style={{ maxHeight : '100%', maxWidth : '100%' }} src={uploadedImageSrc} alt="Your uploaded attachment" />
    //   </Box>
    // );
  }

  return (
    <>
      {uploadError && <ErrorCallout>{uploadError}</ErrorCallout>}
      <Dropzone
        accept={{
          'image/png' : [ '.png' ],
          'image/jpeg' : [ '.jpeg' ],
        }}
        multiple={false}
        onDrop={onDrop}
      >
        {({
          getRootProps, getInputProps, isFocused, isDragAccept, isDragReject,
        }) => (
          <section>
            <div
              {...getRootProps()}
              className={twMerge(
                'flex flex-col items-center p-5 border border-dashed ',
                !isFocused && 'border-[var(--gray-7)] text-[var(--gray-11)] bg-[var(--gray-2)]',
                isFocused && 'border-[var(--gray-8)] text-[var(--gray-12)] bg-[var(--gray-3)]',
                isDragAccept && 'border-[var(--lime-7)] text-[var(--lime-11)]',
                isDragReject && 'border-[var(--red-7)] text-[var(--red-11)]',
              )}
            >
              <input {...getInputProps()} disabled={loading} />
              <Spinner size="3" loading={loading}>
                <p>Drag and drop a file here, or click to select a file</p>
                <p>File will automatically upload.</p>
              </Spinner>
            </div>
          </section>
        )}
      </Dropzone>
    </>
  );
}
