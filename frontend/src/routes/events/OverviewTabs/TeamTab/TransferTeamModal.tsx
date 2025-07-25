import {
  Button,
  Select,
  Text,
  TextField,
} from '@radix-ui/themes';
import Modal from 'components/Modal';
import { map } from 'lodash';
import { useState } from 'react';
import { TbArrowRight } from 'react-icons/tb';

type memberListType = {
  id: string,
  name: string,
}

interface TransferTeamModalProps {
  transferCaptain: boolean,
  membersList: Array<memberListType>,
}

export default function TransferTeamModal({ transferCaptain, membersList }: TransferTeamModalProps) {
  const [ newCaptain, setNewCaptain ] = useState<string>('');
  const [ inviteCode, setInviteCode ] = useState<string>('');

  const transferTeam = async () => {
    console.log('transferTeam action', newCaptain, inviteCode);
    // action for selecting a new captain
    // action for leaving team
  };

  return (
    <Modal
      title="Are you sure you want to transfer teams?"
      description="You will no longer have access to participate with this team, and will be moved to a new team."
      submitVerb="Transfer"
      onSubmit={transferTeam}
      trigger={(
        <Button variant="soft" color="lime">
          <TbArrowRight />
          Transfer Team
        </Button>
      )}
      onOpenChange={(open) => {
        if (open) {
          // reset state when modal is closed and reopened
          setNewCaptain('');
          setInviteCode('');
        }
      }}
      submitDisabled={(transferCaptain && newCaptain === '') || inviteCode === ''}
    >
      <>
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
        <Text>{'Enter your new team\'s invite code to transfer teams.'}</Text>
        <TextField.Root
          placeholder="Invite Code"
          defaultValue=""
          onChange={(e) => setInviteCode(e.target.value)}
        />
      </>
    </Modal>
  );
}
