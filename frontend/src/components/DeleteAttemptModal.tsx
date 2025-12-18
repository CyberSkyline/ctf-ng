import { COLOR_NEGATIVE } from '@/constants';
import { deleteAttempt } from '@/hooks/scoring';
import type { Attempt } from '@/types';
import { Button } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbTrash } from 'react-icons/tb';

export default function DeleteAttemptModal({ attempt }: {attempt: Attempt}) {
  return (
    <Modal
      title="Delete Attempt?"
      description="Are you sure you want to delete this attempt? This action cannot be undone."
      trigger={(
        <Button variant="ghost" color={COLOR_NEGATIVE} className="!m-0 !mt-1.5">
          <TbTrash />
          Delete
        </Button>
      )}
      submitVerb="Delete"
      submitColor={COLOR_NEGATIVE}
      onSubmit={async () => deleteAttempt(attempt.id, attempt.event_id, attempt.challenge_id, attempt.team_id)}
    />
  );
}
