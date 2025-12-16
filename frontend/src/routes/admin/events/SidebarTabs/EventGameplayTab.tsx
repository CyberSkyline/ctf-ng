import type { Event } from '@/types';
import { Flex } from '@radix-ui/themes';
import Statistic from 'components/Statistic';

export default function EventGameplayTab({ event }: {event: Event}) {
  return (
    <Flex direction="column" gap="3">
      <Statistic label="Max Team Size" value={event.max_team_size} />
      <Statistic label="Event Starts" value={event.start_time?.toLocaleString() || 'N/A'} />
      <Statistic label="Event Ends" value={event.end_time?.toLocaleString() || 'N/A'} />
      <Statistic label="Time Limit" value={event.time_limit_minutes ? `${event.time_limit_minutes} minutes` : 'N/A'} />
      <Statistic label="Hints Enabled" value={event.hints_enabled ? 'Yes' : 'No'} />
      <Statistic label="Leaderboard Visible" value={event.show_leaderboard ? 'Yes' : 'No'} />
    </Flex>
  );
}
