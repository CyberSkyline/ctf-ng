import { Button, Select } from '@radix-ui/themes';
import { Form } from 'radix-ui';
import Modal from 'components/Modal';
import { map } from 'lodash';
import { useState } from 'react';
import { TbDoorExit } from 'react-icons/tb';
import { useNavigate } from 'react-router';
import { COLOR_NEGATIVE } from '@/constants';
import { leaveMyTeam } from '@/hooks/events';
import type { Event, TeamMember } from '@/types';

interface LeaveTeamModalProps {
  eventId: Event['id'],
  transferCaptain: boolean,
  membersList: TeamMember[],
}

export default function LeaveTeamModal({ eventId, transferCaptain, membersList }: LeaveTeamModalProps) {
  const [ newCaptain, setNewCaptain ] = useState<string>('');
  const navigate = useNavigate();

  const leaveTeam = async () => leaveMyTeam(eventId, Number(newCaptain)).then(() => {
    navigate('/events');
  });

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
      <Form.Field name="newCaptain" className="flex flex-col w-full">
        <Form.Label>
          All teams must have at least one captain. Please select a new captain before leaving.
        </Form.Label>
        <Form.Control asChild>
          <Select.Root
            onValueChange={setNewCaptain}
          >
            <Select.Trigger placeholder="Select a member" />
            <Select.Content position="popper">
              <Select.Group>
                {map(membersList, (member: { id: string, user_name: string}) => (
                  <Select.Item key={member.id} value={String(member.id)}>{member.user_name}</Select.Item>
                ))}
              </Select.Group>
            </Select.Content>
          </Select.Root>
        </Form.Control>
      </Form.Field>
      )}
    </Modal>
  );
}
