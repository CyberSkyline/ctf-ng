import { COLOR_WARNING } from '@/constants';
import { updateChallenge, useAdminChallengeYaml } from '@/hooks/challenge';
import { Button } from '@radix-ui/themes';
import ChallengeForm from 'components/ChallengeForm';
import Modal from 'components/Modal';
import { TbPencil } from 'react-icons/tb';

export default function ChallengeUpdateModal({ challengeId }: { challengeId: number }) {
  const { data : yaml, error, isLoading } = useAdminChallengeYaml(challengeId);

  return (
    <Modal
      title="Update Challenge"
      trigger={(
        <Button variant="soft" color={COLOR_WARNING} disabled={!!error || isLoading}>
          <TbPencil />
          Update
        </Button>
      )}
      submitVerb="Update"
      submitColor={COLOR_WARNING}
      onSubmit={async (data: {yaml: string}) => {
        if (yaml?.yaml !== data.yaml) {
          // if the yaml has changed, update it
          return updateChallenge(challengeId, data.yaml);
        }
        return Promise.resolve();
      }}
      defaultValues={{
        yaml : yaml?.yaml,
      }}
      className="!max-w-[80ch]"
    >
      {(rhf) => (
        <ChallengeForm rhf={rhf} />
      )}
    </Modal>
  );
}
