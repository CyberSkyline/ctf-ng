import { COLOR_POSITIVE } from '@/constants';
import { createChallenge } from '@/hooks/challenge';
import { Button } from '@radix-ui/themes';
import Modal from 'components/Modal';
import YamlEditor from 'components/YamlEditor';
import { Controller } from 'react-hook-form';
import { TbPlus } from 'react-icons/tb';

export default function ChallengeUploadModal({ eventId }: { eventId: number }) {
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
      onSubmit={async ({ yaml }: {yaml: string}) => {
        if (!yaml) throw new Error('No file content to submit');
        return createChallenge(eventId, yaml);
      }}
      className="!max-w-[80ch]"
    >
      {({ control }) => (
        <Controller
          control={control}
          name="yaml"
          render={
            ({ field }) => (
              <YamlEditor
                value={field.value}
                onChange={field.onChange}
                ref={field.ref}
              />
            )
          }
        />
      )}
    </Modal>
  );
}
