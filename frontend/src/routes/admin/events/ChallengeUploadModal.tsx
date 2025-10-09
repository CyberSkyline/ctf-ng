import { COLOR_POSITIVE } from '@/constants';
import { createChallenge } from '@/hooks/challenge';
import {
  Button,
  Callout,
  Code,
  Heading,
  Text,
} from '@radix-ui/themes';
import Modal from 'components/Modal';
import { useState } from 'react';
import Dropzone from 'react-dropzone';
import { TbPlus, TbUpload } from 'react-icons/tb';

export default function ChallengeUploadModal({ eventId }: { eventId: number }) {
  const [ fileContent, setFileContent ] = useState<string | null>(null);

  return (
    <Modal
      title="Add Challenge"
      description="Upload a challenge YAML file to create a new challenge for this event."
      trigger={(
        <Button variant="soft" color={COLOR_POSITIVE}>
          <TbPlus />
          Add
        </Button>
      )}
      submitVerb="Upload"
      submitDisabled={!fileContent}
      onSubmit={async () => {
        if (!fileContent) throw new Error('No file content to submit');
        return createChallenge(eventId, fileContent).then(() => {
          setFileContent(null);
        });
      }}
      onOpenChange={(open) => {
        if (open) {
          setFileContent(null);
        }
      }}
    >
      <Dropzone
        onDrop={(files) => {
          if (files.length > 0) {
            const file = files[0];
            file.text().then((content) => {
              setFileContent(content);
            }).catch(() => {
              setFileContent(null);
            });
          }
        }}
        accept={{
          'application/yaml' : [ '.yaml', '.yml' ],
        }}
        multiple={false}
      >
        {({ getRootProps, getInputProps, isDragActive }) => (
          <Callout.Root
            {...getRootProps()}
            variant={(isDragActive) ? 'surface' : 'outline'}
            className="cursor-pointer !p-8 !flex flex-col !items-center"
          >
            <input
              {...getInputProps()}
              name="file"
            />
            <Heading size="6"><TbUpload /></Heading>
            <Text>Drag and drop a YAML file here, or click to select one.</Text>
          </Callout.Root>
        )}
      </Dropzone>

      {fileContent && (
        <Code className="block !p-2 whitespace-pre-wrap !h-64 overflow-auto" color="gray">
          {fileContent}
        </Code>
      )}
    </Modal>
  );
}
