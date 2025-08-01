import { COLOR_NEGATIVE } from '@/constants';
import { Button, Select, Text } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { map } from 'lodash';
import { useState } from 'react';
import { TbDoorExit } from 'react-icons/tb';

type memberListType = {
  id: string,
  name: string,
}

interface LeaveTeamModalProps {
  transferCaptain: boolean,
  membersList: Array<memberListType>,
}

export default function LeaveTeamModal({ transferCaptain, membersList }: LeaveTeamModalProps) {
  const [ newCaptain, setNewCaptain ] = useState<string>('');

  const leaveTeam = async () => {
    console.log('leaveTeam action', newCaptain);
    // action for selecting a new captain
    // action for leaving team
  };

  return (
    <Modal
      title="Are you sure you want to leave the team?"
      description="You will no longer have access to participate with this team."
      trigger={(
        <Button variant="soft" color={COLOR_NEGATIVE}>
          <TbDoorExit />
          Leave Team
        </Button>
      )}
      onSubmit={leaveTeam}
      onOpenChange={(open) => {
        if (open) {
          // reset captain state when modal is closed and reopened
          setNewCaptain('');
        }
      }}
      submitVerb="Leave"
      submitColor={COLOR_NEGATIVE}
      submitDisabled={transferCaptain && newCaptain === ''}
    >
      {transferCaptain && (
      <>
        <Text>
          All teams must have at least one captain. Please select a new captain before leaving.
        </Text>

        <Select.Root
          defaultValue=""
          onValueChange={setNewCaptain}
        >
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
    </Modal>
  );
}
