import type { Event } from '@/types';
import {
  AspectRatio,
  Box,
  Flex,
  Heading,
} from '@radix-ui/themes';
import type { ReactNode } from 'react';
import { TbCalendar, TbUser } from 'react-icons/tb';
import EventBadge from './EventBadge';
import RadixMarkdown from './RadixMarkdown';

export default function EventHeader({
  children = undefined,
  event,
}: {
  children?: ReactNode;
  event: Event;
}) {
  const {
    name, description, start_time : startTime, end_time : endTime,
  } = event;

  const now = new Date();

  let state: 'upcoming' | 'live' | 'ended' | 'waiting' | null = null;
  if (endTime && now > endTime) {
    state = 'ended';
  } else if (!startTime || now < startTime) {
    state = 'upcoming';
  } else if (startTime && endTime && now >= startTime && now <= endTime) {
    state = 'live';
  }

  return (
    <Flex direction="row" gap="6" align="start">
      <Box className="w-32" flexShrink="0">
        <AspectRatio ratio={3 / 4}>
          {/* Placeholder for event card image */}
          <Box className="h-full w-full bg-[var(--lime-8)] rounded-lg shadow-xl" />
        </AspectRatio>
      </Box>
      <Flex direction="column" flexGrow="1" align="start" gap="2">
        {state && (
          <EventBadge state={state} />
        )}
        <Box>
          <Heading size="8">{name}</Heading>
          <RadixMarkdown>
            {description || ''}
          </RadixMarkdown>
        </Box>
        <Flex direction="row" gap="2" align="center">
          {dateRange && (
          <Text as="span" color="gray">
            <TbCalendar className="inline me-1" title="Date range" />
            {dateRange}
          </Text>
          )}
          {maxTeamSize && (
            <Text as="span" color="gray">
              <TbUser className="inline me-1" />
              {maxTeamSize === 1 ? 'Individual' : `Teams of 2-${maxTeamSize}`}
            </Text>
          )}
        </Flex>
        {children}
      </Flex>
    </Flex>
  );
}
