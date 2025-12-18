import { COLOR_NEGATIVE } from '@/constants';
import { deleteAttempt } from '@/hooks/scoring';
import type { Attempt } from '@/types';
import { Button, DataList } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbTrash } from 'react-icons/tb';

export default function DeleteAttemptModal({ attempt }: {attempt: Attempt}) {
  return (
    <Modal
      title="Delete Attempt?"
      description="Are you sure you want to delete the following attempt? This action cannot be undone."
      trigger={(
        <Button variant="ghost" color={COLOR_NEGATIVE} className="!m-0 !mt-1.5">
          <TbTrash />
          Delete
        </Button>
      )}
      submitVerb="Delete"
      submitColor={COLOR_NEGATIVE}
      onSubmit={async () => deleteAttempt(attempt.id, attempt.event_id, attempt.challenge_id, attempt.team_id)}
    >
      <DataList.Root>
        <DataList.Item>
          <DataList.Label>Challenge</DataList.Label>
          <DataList.Value>{attempt.challenge_name}</DataList.Value>
        </DataList.Item>
        <DataList.Item>
          <DataList.Label>Team</DataList.Label>
          <DataList.Value>{attempt.team_name}</DataList.Value>
        </DataList.Item>
        <DataList.Item>
          <DataList.Label>User</DataList.Label>
          <DataList.Value>{attempt.user_name}</DataList.Value>
        </DataList.Item>
        <DataList.Item>
          <DataList.Label>Submission</DataList.Label>
          <DataList.Value>{attempt.submission}</DataList.Value>
        </DataList.Item>
        <DataList.Item>
          <DataList.Label>Correct</DataList.Label>
          <DataList.Value>{attempt.is_correct ? 'Yes' : 'No'}</DataList.Value>
        </DataList.Item>
      </DataList.Root>
    </Modal>
  );
}
