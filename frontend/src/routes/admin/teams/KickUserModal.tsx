import { COLOR_NEGATIVE } from '@/constants';
import { adminKickTeamMember } from '@/hooks/team';
import type { TeamMember } from '@/types';
import { Button, Text } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbDoorExit } from 'react-icons/tb';

export default function KickUserModal({ member, solo }: { member: TeamMember, solo: boolean }) {
  if (member.role === 'captain' && !solo) {
    return (
      <Text color="gray">
        Assign a new captain before removing this user.
      </Text>
    );
  }

  return (
    <Modal
      title="Remove User?"
      description={`Are you sure you want to remove ${member.user_name} from the team? They will need to re-register for the event to participate.`}
      onSubmit={async () => adminKickTeamMember(member.team_id, member.user_id)}
      submitColor={COLOR_NEGATIVE}
      submitVerb="Remove"
      trigger={(
        <Button variant="ghost" color={COLOR_NEGATIVE}>
          <TbDoorExit />
          Remove
        </Button>
       )}
    />
  );
}
