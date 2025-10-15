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
import gameCardOffensive from 'assets/offensive.png';
import gameCardTeam from 'assets/teams.png';
import EventBadge from 'components/EventBadge';
import { TbCalendarEvent, TbClock } from 'react-icons/tb';
import { Link } from 'react-router';

export default function EventCard({ event }: { event: Event }) {
  const individual = event.max_team_size === 1;

  return (
    <Card asChild>
      <Link to={`/events/${event.id}`}>
        <Flex direction="row" gap="4">
          <Inset side="left" className="w-32 shrink-0 shadow">
            <img src={event.max_team_size === 1 ? gameCardOffensive : gameCardTeam} alt={`Card for ${event.name}`} />
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
                    // @ts-expect-error - Intl.DurationFormat is baseline-supported, but TS doesn't like it
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
