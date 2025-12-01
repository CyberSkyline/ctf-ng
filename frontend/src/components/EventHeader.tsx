import type { Event } from '@/types';
import {
  Box,
  Flex,
  Heading,
  Text,
} from '@radix-ui/themes';
import { isNull } from 'lodash';
import type { ReactNode } from 'react';
import { TbCalendar, TbUser } from 'react-icons/tb';
import EventBadge from './EventBadge';
import EventGraphic from './EventGraphic';
import RadixMarkdown from './RadixMarkdown';

export default function EventHeader({
  children = undefined,
  event,
}: {
  children?: ReactNode;
  event: Event;
}) {
  const {
    id,
    name,
    description,
    start_time : startTime,
    end_time : endTime,
    max_team_size : maxTeamSize,
  } = event;

  const dateRange = (!isNull(startTime) && !isNull(endTime)) && `${startTime?.toLocaleString()} - ${endTime?.toLocaleString()}`;

  return (
    <Flex direction="row" gap="6" align="start">
      <EventGraphic event={event} className="w-48 shrink-0 rounded-lg shadow-xl" />
      <Flex direction="column" flexGrow="1" align="start" gap="2">
        <EventBadge eventId={id} size="3" />
        <Box>
          <Heading size="8">
            {name}
          </Heading>
          <RadixMarkdown>
            {description || ''}
          </RadixMarkdown>
        </Box>
        <Flex direction="column" gap="1">
          {dateRange && (
            <Text color="gray">
              <TbCalendar className="inline me-1" title="Date range" />
              {dateRange}
            </Text>
          )}
          {maxTeamSize && (
            <Text color="gray">
              <TbUser className="inline me-1" />
              {maxTeamSize === 1
                ? 'Individual'
                : `Teams of ${maxTeamSize === 2 ? '2' : `2-${maxTeamSize}`}`}
            </Text>
          )}
        </Flex>
        {children}
      </Flex>
    </Flex>
  );
}
