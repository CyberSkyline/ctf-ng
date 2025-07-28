import { Button, TextField } from '@radix-ui/themes';
import Modal from 'components/Modal';

interface AddMemberModalProps {
  inviteCode: string,
}

export default function AddMemberModal({ inviteCode }: AddMemberModalProps) {
  const inviteURL = `${window.location.origin}/teamSetup/invite/${inviteCode}`;

  return (
    <Modal
      trigger={(<Button className="!max-w-32">Add Member</Button>)}
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
            type="button"
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
