import { COLOR_NEGATIVE } from '@/constants';
import { leaveMyTeam, useMyTeamMembers } from '@/hooks/events';
import { useCurrentUser } from '@/hooks/users';
import type { Event } from '@/types';
import { Button, Tooltip } from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import Modal from 'components/Modal';
import { TbDoorExit } from 'react-icons/tb';
import { useNavigate } from 'react-router';

export default function LeaveTeamModal({ event }: { event: Event }) {
  const navigate = useNavigate();
  const { data : members } = useMyTeamMembers(event.id);
  const { data : currentUser } = useCurrentUser();
  const isIndividual = event.max_team_size === 1;
  const transferCaptain = !!members && !!currentUser && members.length > 1 && members.find((member) => member.user_id === currentUser.id)?.role === 'captain';

  const leaveTeam = async () => {
    leaveMyTeam(event.id).then(() => {
      navigate('/events');
    });
  };

  const btn = (
    <Button variant="ghost" color={COLOR_NEGATIVE} disabled={!members || transferCaptain}>
      <TbDoorExit />
      {isIndividual ? 'Unregister' : 'Leave Team'}
    </Button>
  );

  return (
    <Modal
      title={isIndividual ? 'Unregister from Event' : 'Leave Team'}
      description={`Are you sure you want to ${isIndividual ? 'unregister' : 'leave this team'}?
        You will no longer have access to participate in this event unless you register again.`}
      trigger={transferCaptain ? (
        <Tooltip
          content="You must assign a new captain before leaving the team."
          disableHoverableContent
        >
          {btn}
        </Tooltip>
      ) : btn}
      onSubmit={leaveTeam}
      submitVerb={isIndividual ? 'Unregister' : 'Leave Team'}
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
