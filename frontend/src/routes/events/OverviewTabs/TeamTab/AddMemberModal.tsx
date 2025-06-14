import { useState } from 'react';
import {
  Box,
  Button,
  Dialog,
  Flex,
  TextField,
} from '@radix-ui/themes';
import { FaXmark } from 'react-icons/fa6';

interface AddMemberModalProps {
  inviteCode: string,
}

export default function AddMemberModal({ inviteCode }: AddMemberModalProps) {
  const [open, setOpen] = useState<boolean>(false);
  const inviteURL = `${window.location.origin}/teamSetup/invite/${inviteCode}`;

  return (
    <Box maxWidth="200px">
      <Dialog.Root open={open} onOpenChange={setOpen}>
        <Dialog.Trigger>
          <Button>Add Member</Button>
        </Dialog.Trigger>

        <Dialog.Content aria-describedby={undefined}>
          <Flex direction="row">
            <Dialog.Title
              className="pb-2"
            >
              Invite Members by shaing this link.
            </Dialog.Title>
            <Dialog.Close>
              <button type="button" aria-label="Close" className="absolute left-auto right-4 top-4">
                <FaXmark />
              </button>
            </Dialog.Close>
          </Flex>
          <Flex mb="3" direction="column">
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
          </Flex>
        </Dialog.Content>
      </Dialog.Root>
    </Box>
  );
}
