import { useState } from 'react';
import { map } from 'lodash';
import {
  Flex,
  Text,
  TextField,
  Select,
} from '@radix-ui/themes';
import Modal from 'components/Modal';

type memberListType = {
  id: string,
  name: string,
}

interface TransferTeamModalProps {
  transferCaptain: boolean,
  membersList: Array<memberListType>,
}

export default function TransferTeamModal({ transferCaptain, membersList }: TransferTeamModalProps) {
  const [newCaptain, setNewCaptain] = useState<string | undefined>(undefined);
  const [inviteCode, setInviteCode] = useState<string>('');

  function transferTeam() {
    console.log('transferTeam action', newCaptain, inviteCode);
    // action for selecting a new captain
    // action for leaving team
  }

  return (
    <Modal
      title="Are you sure you want to transfer teams?"
      buttonText="Transfer Team"
      onSubmit={transferTeam}
      onSubmitText="Submit"
    >
      <Flex gap="4" direction="column">
        {transferCaptain && (
          <>
            <Text>
              All teams must have at least one captain.
            </Text>
            <Text>
              Please select a new captain before transferring.
            </Text>
            <Select.Root defaultValue="" onValueChange={setNewCaptain}>
              <Select.Trigger placeholder="Select a member" />
              <Select.Content position="popper">
                <Select.Group>
                  {map(membersList, (member: { id: string, name: string}) => (
                    <Select.Item key={member.id} value={member.id}>{member.name}</Select.Item>
                  ))}
                </Select.Group>
              </Select.Content>
            </Select.Root>
          </>
        )}
        <TextField.Root
          placeholder="Invite Code"
          defaultValue=""
          onChange={(e) => setInviteCode(e.target.value)}
        />
      </Flex>
    </Modal>
  );
}
