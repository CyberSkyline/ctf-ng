import { TeamIcon, UserIcon } from '@/constants';
import type { Event } from '@/types';
import {
  Box,
  Card,
  Flex,
  Heading,
  Inset,
  Text,
} from '@radix-ui/themes';
import EventBadge from 'components/EventBadge';
import EventGraphic from 'components/EventGraphic';
import { TbCalendarEvent, TbClock } from 'react-icons/tb';
import { Link } from 'react-router';

export default function EventCard({ event }: { event: Event }) {
  const individual = event.max_team_size === 1;

  return (
    <Card asChild>
      <Link to={`/events/${event.id}`}>
        <Flex direction="row" gap="4" className="h-full">
          <Inset side="left" className="empty:hidden shrink-0">
            <EventGraphic event={event} className="w-32 shadow !rounded-none" />
          </Inset>
          <Flex direction="column" gap="2" className="flex-grow" justify="between">
            <Box>
              <Heading size="4">{event.name}</Heading>
              <EventBadge eventId={event.id} size="2" className="mt-2" />
            </Box>
            <Flex direction="column">
              <Text size="2" color="gray">
                {individual ? (
                  <>
                    <UserIcon className="inline" />
                    {' '}
                    Individual
                  </>
                ) : (
                  <>
                    <TeamIcon className="inline" />
                    {` Teams of 2${event.max_team_size > 2 ? `-${event.max_team_size}` : ''}`}
                  </>
                )}
              </Text>

              { event.start_time && (
                <Text size="2" color="gray">
                  <TbCalendarEvent className="inline" aria-label="Event start time" />
                  {' '}
                  {event.start_time?.toLocaleString([], {
                    year : 'numeric', month : 'numeric', day : 'numeric', hour : '2-digit', minute : '2-digit',
                  })}
                </Text>
              ) }

              { event.time_limit_minutes && (
                <Text size="2" color="gray">
                  <TbClock className="inline" aria-label="Event time limit" />
                  {' '}
                  {
                    new Intl.DurationFormat('en')
                      .format({
                        hours : Math.floor(event.time_limit_minutes / 60),
                        minutes : event.time_limit_minutes % 60,
                      })
                  }
                </Text>
              ) }
            </Flex>
          </Flex>
        </Flex>
      </Link>
    </Card>
  );
}
