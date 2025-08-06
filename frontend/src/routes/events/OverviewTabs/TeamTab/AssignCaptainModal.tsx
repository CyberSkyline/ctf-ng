import { Button } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbStar } from 'react-icons/tb';
import { COLOR_WARNING } from '@/constants';
import type { Event, TeamMember } from '@/types';
import { promoteMyCaptain } from '@/hooks/events';

interface AssignCaptainModalProps {
  eventId: Event['id'],
  userId: TeamMember['user_id'],
  name: TeamMember['user_name'],
}

export default function AssignCaptainModal({ eventId, userId, name }:AssignCaptainModalProps) {
  const assignCaptain = async () => promoteMyCaptain(eventId, userId);

  return (
    <Modal
      title={`Are you sure you want to assign ${name}?`}
      description="You will no longer be a Team Captain. By assigning a new member as Team Captain, you will lose your ability to add and remove team members."
      trigger={(
        <Button variant="soft" color={COLOR_WARNING}>
          <TbStar />
          Assign Captain
        </Button>
      )}
      onSubmit={assignCaptain}
      submitVerb="Assign"
      submitColor={COLOR_WARNING}
    />
  );
}
