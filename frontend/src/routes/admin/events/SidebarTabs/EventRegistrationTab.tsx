import type { Event } from '@/types';
import { Flex } from '@radix-ui/themes';
import Statistic from 'components/Statistic';

export default function EventRegistrationTab({ event }: {event: Event}) {
  return (
    <Flex direction="column" gap="3">
      <Statistic label="Visibility" value={event.public ? 'Public' : 'Private'} />
      <Statistic label="Registration Open" value={event.registration_open ? 'Yes' : 'No'} />
      <Statistic label="Registration Starts" value={event.registration_start_date?.toLocaleString() || 'N/A'} />
      <Statistic label="Registration Ends" value={event.registration_end_date?.toLocaleString() || 'N/A'} />
      <Statistic label="Allow Team Management" value={event.locked ? 'No' : 'Yes'} />
    </Flex>
  );
}
