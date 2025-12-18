import { COLOR_POSITIVE } from '@/constants';
import { createChallenge } from '@/hooks/challenge';
import { Button } from '@radix-ui/themes';
import ChallengeForm from 'components/ChallengeForm';
import Modal from 'components/Modal';
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
      {(rhf) => (
        <ChallengeForm rhf={rhf} />
      )}
    </Modal>
  );
}
