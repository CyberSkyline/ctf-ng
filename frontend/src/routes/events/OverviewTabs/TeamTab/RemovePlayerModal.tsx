import { Button } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbCircleMinus } from 'react-icons/tb';
import { COLOR_NEGATIVE } from '@/constants';
import type { Event, TeamMember } from '@/types';
import { kickFromMyTeam } from '@/hooks/events';

interface RemovePlayerModalProps {
  eventId: Event['id'],
  userId: TeamMember['user_id'],
  name: TeamMember['user_name'],
}

export default function RemovePlayerModal({ eventId, userId, name }:RemovePlayerModalProps) {
  const removePlayer = async () => kickFromMyTeam(eventId, userId);

  return (
    <Modal
      title={`Are you sure you want to remove ${name}?`}
      description="They will no longer have access to participate with this team. The invite code for the team will change."
      trigger={(
        <Button variant="soft" color={COLOR_NEGATIVE}>
          <TbCircleMinus />
          Remove Player
        </Button>
      )}
      onSubmit={removePlayer}
      submitVerb="Remove"
      submitColor={COLOR_NEGATIVE}
    />
  );
}
