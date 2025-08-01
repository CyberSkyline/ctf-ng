import {
  COLOR_INFO,
  COLOR_NEGATIVE,
  COLOR_POSITIVE,
  COLOR_WARNING,
  type AccentColor,
} from '@/constants';
import { useEvent } from '@/hooks/events';
import type { Team } from '@/types';
import { Badge } from '@radix-ui/themes';

function getBadgeColor(memberCount: number, maxTeamSize: number): AccentColor {
  if (memberCount === 0 || memberCount > maxTeamSize) {
    return COLOR_NEGATIVE; // Team is empty or is over-filled
  }

  if (maxTeamSize > 1 && memberCount === 1) {
    return COLOR_NEGATIVE; // Single-member team where 2+ members are required
  }

  if (maxTeamSize > 1 && memberCount === maxTeamSize) {
    return COLOR_WARNING; // Full team
  }

  return (maxTeamSize === 1) ? COLOR_INFO : COLOR_POSITIVE; // Valid, individual teams get a distinct color
}

export default function MemberCountBadge({ team }: { team: Team }) {
  const { data : event, error } = useEvent(team.event_id);

  if (error) {
    return <Badge variant="soft" color={COLOR_NEGATIVE}>Error</Badge>;
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
