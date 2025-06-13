import { Grid, Heading } from '@radix-ui/themes';
import type { accentColors } from '@radix-ui/themes/props';
import EventCard from 'components/event/EventCard';

export default function PastEvents({ events }: {
    events: {
        id: string;
        name: string;
        description: string;
        color?: typeof accentColors[number];
    }[]
}) {
  if (events.length === 0) {
    return null;
  }

  return (
    <>
      <Heading size="6">Your Past Events</Heading>
      <Grid
        columns={{
          initial: '1', xs: '1', sm: '2', lg: '3',
        }}
        gap="4"
      >
        {events.map((event) => (
          <EventCard
            key={event.id}
            id={event.id}
            name={event.name}
            description={event.description}
            color={event.color}
          />
        ))}
      </Grid>
    </>
  );
}
