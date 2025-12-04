import { COLOR_POSITIVE } from '@/constants';
import { Button } from '@radix-ui/themes';
import Dropzone from 'react-dropzone';
import { TbUpload } from 'react-icons/tb';

export default function UploadButton({ onDrop, loading }: { onDrop: (acceptedFiles: File[]) => void; loading: boolean }) {
  return (
    <Dropzone
      accept={{
        'image/png' : [ '.png' ],
        'image/jpeg' : [ '.jpeg' ],
      }}
      multiple={false}
      onDrop={onDrop}
      disabled={loading}
    >
      {({
        getRootProps, getInputProps,
      }) => (
        <Button
          {...getRootProps()}
          color={COLOR_POSITIVE}
          loading={loading}
          variant="soft"
          type="button"
        >
          <input {...getInputProps()} />
          <TbUpload aria-label="Upload" />
        </Button>
      )}
    </Dropzone>
  );
}
