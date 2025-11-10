import Dropzone from "react-dropzone";
import { twMerge } from "tailwind-merge";

/*
TODO:
This s3 bucket setup isn't finished, so this is just a visual field and error/success states
We need to hook this up to the s3 bucket, then pass the generated url for the image upload to the parent form

*/

export default function NewLogoDropzone() {
  return (
    <Dropzone
      accept={{
        'image/png': ['.png'],
        'image/jpeg': ['.jpeg'],
      }}
      multiple={false}
    >
      {({ getRootProps, getInputProps, isFocused, isDragAccept, isDragReject, acceptedFiles }) => (
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
            <input {...getInputProps()} />
            <p>Drag 'n drop a file here, or click to select a file</p>
          </div>
          
          {/* This dropdown only accepts one file at a time. */}
          <p className='pt-2'>File:</p>
          <p>{acceptedFiles[0]?.path}</p>
        </section>
      )}
    </Dropzone>
  )
}