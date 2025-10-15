import { COLOR_WARNING } from '@/constants';
import { adminPromoteTeamMember } from '@/hooks/team';
import type { TeamMember } from '@/types';
import { Button } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbStar } from 'react-icons/tb';

export default function PromoteUserModal({ member }: { member: TeamMember }) {
  return (
    <Modal
      title="Assign new captain?"
      description={`This will make ${member.user_name} the new team captain. The current captain will be demoted.`}
      onSubmit={async () => adminPromoteTeamMember(member.team_id, member.user_id)}
      submitColor={COLOR_WARNING}
      submitVerb="Assign"
      trigger={(
        <Button variant="ghost" color={COLOR_WARNING} disabled={member.role === 'captain'}>
          <TbStar />
          Assign Captain
        </Button>
       )}
    />
  );
}
