import { Button } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbDoorExit } from 'react-icons/tb';
import { useNavigate } from 'react-router';
import { COLOR_NEGATIVE } from '@/constants';
import { leaveMyTeam } from '@/hooks/events';
import type { Event } from '@/types';
import { ErrorCallout } from 'components/Callouts';

interface LeaveTeamModalProps {
  eventId: Event['id'],
  transferCaptain: boolean,
}

export default function LeaveTeamModal({ eventId, transferCaptain }: LeaveTeamModalProps) {
  const navigate = useNavigate();

  const leaveTeam = async () => {
    leaveMyTeam(eventId).then(() => {
      navigate('/events');
    });
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
      submitVerb="Leave"
      submitColor={COLOR_NEGATIVE}
      submitDisabled={transferCaptain}
    >
      {transferCaptain && (
        <ErrorCallout>
          You must assign a new captain prior to leaving the team.
        </ErrorCallout>
      )}
    </Modal>
  );
}
