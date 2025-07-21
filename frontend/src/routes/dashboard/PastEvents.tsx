import type { Event } from '@/types';
import { Grid, Heading } from '@radix-ui/themes';
import EventCard from './EventCard';

export default function PastEvents({ events }: {
    events: Event[]
}) {
  if (events.length === 0) {
    return null;
  }

  return (
    <>
      <Heading size="6">Your Past Events</Heading>
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
