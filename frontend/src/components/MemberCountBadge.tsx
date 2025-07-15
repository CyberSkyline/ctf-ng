import { useEvent } from '@/hooks/events';
import type { Team } from '@/types';
import { Badge } from '@radix-ui/themes';
import type { accentColors } from '@radix-ui/themes/props';

function getBadgeColor(memberCount: number, maxTeamSize: number): (typeof accentColors)[number] {
  if (memberCount === 0 || memberCount > maxTeamSize) {
    return 'red'; // Team is empty or is over-filled
  }

  if (maxTeamSize > 1 && memberCount === 1) {
    return 'red'; // Single-member team where 2+ members are required
  }

  if (maxTeamSize > 1 && memberCount === maxTeamSize) {
    return 'amber'; // Full team
  }

  return (maxTeamSize === 1) ? 'jade' : 'lime'; // Valid, individual teams get a distinct color
}

export default function MemberCountBadge({ team }: { team: Team }) {
  const { data : event, error } = useEvent(team.event_id);

  if (error) {
    return <Badge variant="soft" color="red">ERR</Badge>;
  }

  return (
    event && (
    <Badge variant="soft" color={getBadgeColor(team.member_count, event.max_team_size)} size="2">
      {team.member_count}
      /
      {event.max_team_size}
    </Badge>
    )
  );
}
