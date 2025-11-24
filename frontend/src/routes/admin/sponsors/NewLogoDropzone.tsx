import { directUpload } from '@/hooks/fileuploads';
import Dropzone from 'react-dropzone';
import { twMerge } from 'tailwind-merge';
import { useState } from 'react';
import { ErrorCallout } from 'components/Callouts';
import { Spinner } from '@radix-ui/themes';
import type { UseFormSetValue } from 'react-hook-form';
import type { Sponsor } from '@/types';

export default function NewLogoDropzone({setValue}: {setValue: UseFormSetValue<Omit<Sponsor, "id">>}) {
  const [ uploadError, setUploadError ] = useState<string | null>(null)
  const [ loading, setLoading ] = useState<boolean>(false)

  const onDrop = async (acceptedFiles: File[]) => {
    const formData = new FormData() 
    formData.append('folder', 'sponsor-logos')
    formData.append('file', acceptedFiles[0])

    setUploadError(null);
    directUpload(formData).then((data) => {
      setValue('logo', data.filename)
    }).catch(err => setUploadError(err.message))
    .finally(() => setLoading(false));
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
          getRootProps, getInputProps, isFocused, isDragAccept, isDragReject, acceptedFiles,
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
              <input {...getInputProps()} disabled={loading}/>
              <Spinner size='3' loading={loading}>
                <p>Drag and drop a file here, or click to select a file</p>
                <p>File will automatically upload.</p>
              </Spinner>
            </div>

            {/* This dropdown only accepts one file at a time. */}
            <p className="pt-2">File:</p>
            <p>{acceptedFiles[0]?.path}</p>
          </section>
        )}
      </Dropzone>
    </>
  );
}
