import {
  Button,
  Select,
  Text,
  TextField,
} from '@radix-ui/themes';
import { Form } from 'radix-ui';
import Modal from 'components/Modal';
import { map } from 'lodash';
import { useState } from 'react';
import { TbArrowRight } from 'react-icons/tb';
import { COLOR_WARNING } from '@/constants';
import type { Event, TeamMember } from '@/types';

interface TransferTeamModalProps {
  eventId: Event['id'],
  transferCaptain: boolean,
  membersList: TeamMember[],
}

export default function TransferTeamModal({ eventId, transferCaptain, membersList }: TransferTeamModalProps) {
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
      submitColor={COLOR_WARNING}
      onSubmit={transferTeam}
      trigger={(
        <Button variant="soft" color={COLOR_WARNING}>
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
        <Form.Field name="inviteCode">
          <Form.Label>{'Enter your new team\'s invite code to transfer teams.'}</Form.Label>
          <Form.Control asChild>
            <TextField.Root
              placeholder="Invite Code"
              onChange={(e) => setInviteCode(e.target.value)}
            />
          </Form.Control>
        </Form.Field>
      </>
    </Modal>
  );
}
