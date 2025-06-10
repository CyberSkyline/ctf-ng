import { useState } from 'react';
import { map } from 'lodash';
import {
  Flex,
  Text,
  Select,
} from '@radix-ui/themes';
import Modal from 'components/Modal';

type memberListType = {
  id: string,
  name: string,
}

interface LeaveTeamModalProps {
  transferCaptain: boolean,
  membersList: Array<memberListType>,
}

export default function LeaveTeamModal({ transferCaptain, membersList }: LeaveTeamModalProps) {
  const [newCaptain, setNewCaptain] = useState<string | undefined>(undefined);

  function leaveTeam() {
    console.log('leaveTeam action', newCaptain);
    // action for selecting a new captain
    // action for leaving team
  }

  return (
    <Modal
      title="Are you sure you want to leave the team?"
      buttonText="Leave Team"
      onSubmit={leaveTeam}
      onSubmitText="Leave"
      onSubmitColor="red"
    >
      <Flex gap="4" direction="column">
        {transferCaptain && (
          <>
            <Text>
              All teams must have at least one captain. Please select a new captain before leaving.
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
        <Text>You will no longer have access to participate with this team.</Text>
      </Flex>
    </Modal>
  );
}
