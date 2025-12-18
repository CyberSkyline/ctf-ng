import type { Event } from '@/types';
import { Flex } from '@radix-ui/themes';
import EventGraphic from 'components/EventGraphic';
import RadixMarkdown from 'components/RadixMarkdown';

export default function EventDetailsTab({ event }: {event: Event}) {
  return (
    <Flex direction="column" gap="3">
      <EventGraphic event={event} className="w-64 rounded-lg shadow-lg" />
      <RadixMarkdown>
        {event.description || ''}
      </RadixMarkdown>
    </Flex>
  );
}
