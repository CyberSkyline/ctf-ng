import { COLOR_POSITIVE, ROUTEPREFIX } from '@/constants';
import type { Team } from '@/types';
import { Button, TextField } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbShare } from 'react-icons/tb';

export default function AddMemberModal({ eventId, inviteCode }: { eventId: Team['event_id'], inviteCode : Team['invite_code']}) {
  const inviteURL = `${window.location.origin}${ROUTEPREFIX}/events/${eventId}/invitecode/${inviteCode}`;

  return (
    <Modal
      trigger={(
        <Button
          color={COLOR_POSITIVE}
          variant="soft"
        >
          <TbShare />
          Add Member
        </Button>
      )}
      title="Invite Members"
      description="Invite members to your team by sharing this link."
    >
      <TextField.Root
        size="3"
        value={inviteURL}
        type="text"
        readOnly
      >
        <TextField.Slot pr="3" side="right">
          <Button
            size="1"
            onClick={() => {
              // Clipboard only works in secure context (https)
              navigator.clipboard.writeText(inviteURL);
            }}
          >
            Copy
          </Button>
        </TextField.Slot>
      </TextField.Root>
    </Modal>
  );
}
