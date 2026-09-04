import { Button } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { deleteChallenge } from '@/hooks/challenge';
import { COLOR_NEGATIVE } from '@/constants';
import { TbBan } from 'react-icons/tb';

/*
  This is only available in DEV mode. This action is too destructive for production.
*/
export default function ChallengeDeleteModal({ challengeId, eventId }: { challengeId: number, eventId: number }) {
  return (
    <Modal
      title="Delete Challenge"
      trigger={(
        <Button variant="soft" color={COLOR_NEGATIVE}>
          <TbBan />
          Delete
        </Button>
      )}
      submitVerb="Delete"
      submitColor={COLOR_NEGATIVE}
      onSubmit={async () => {
        return deleteChallenge(challengeId, eventId);
      }}
    >
      Are you sure you want to delete this challenge? This action cannot be undone.
      The following related items will be deleted:
      <ul className="list-disc list-inside">
        <li>Challenge</li>
        <li>Association with an event</li>
        <li>Deployments where the challenge was used</li>
        <li>Announcements</li>
        <li>Challenge History</li>
      </ul>
    </Modal>
  );
}