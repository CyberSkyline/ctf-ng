import type { Event } from '@/types';
import {
  Callout,
  Grid,
  Heading,
  Link as RadixLink,
} from '@radix-ui/themes';
import { TbInfoCircle } from 'react-icons/tb';
import { Link } from 'react-router';
import EventCard from './EventCard';

export default function UpcomingEvents({
  events,
}: {
    events: Event[]
}) {
  const heading = <Heading size="6">Your Upcoming Events</Heading>;

  if (events.length === 0) {
    return (
      <>
        {heading}
        <Callout.Root color="jade" variant="surface">
          <Callout.Icon>
            <TbInfoCircle />
          </Callout.Icon>
          <Callout.Text>
            You are not registered for any upcoming events.
            {' '}
            <RadixLink asChild><Link to="/events">Register for an upcoming event</Link></RadixLink>
            {' '}
            or head to the
            {' '}
            <RadixLink asChild><Link to="/practice">practice area</Link></RadixLink>
            {' '}
            to hone your skills!
          </Callout.Text>
        </Callout.Root>
      </>
    );
  }

  return (
    <>
      {heading}
      <Grid
        columns={{
          initial : '1', xs : '1', sm : '2', lg : '3',
        }}
        gap="4"
      >
        {events.map((event) => (
          <EventCard
            key={event.id}
            event={event}
          />
        ))}
      </Grid>
    </>
  );
}
