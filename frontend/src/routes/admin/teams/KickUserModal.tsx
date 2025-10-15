import { COLOR_NEGATIVE } from '@/constants';
import { adminKickTeamMember } from '@/hooks/team';
import type { TeamMember } from '@/types';
import { Button } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbDoorExit } from 'react-icons/tb';

export default function KickUserModal({ member }: { member: TeamMember }) {
  return (
    <Modal
      title="Remove User?"
      description={`Are you sure you want to remove ${member.user_name} from the team? They will need to re-register for the event to participate.`}
      onSubmit={async () => adminKickTeamMember(member.team_id, member.user_id)}
      submitColor={COLOR_NEGATIVE}
      submitVerb="Remove"
      trigger={(
        <Button variant="ghost" color={COLOR_NEGATIVE} disabled={member.role === 'captain'}>
          <TbDoorExit />
          Remove
        </Button>
       )}
    />
  );
}
