import { useMyEvents } from '@/hooks/events';
import { Grid, Heading } from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import EventCard from './EventCard';

export default function PastEvents() {
  const { data, error } = useMyEvents();
  const pastEvents = data?.filter((event) => event.end_time && new Date() > event.end_time);

  if (error) {
    return (
      <>
        <Heading size="6">Your Past Events</Heading>
        <ErrorCallout>{error.message}</ErrorCallout>
      </>
    );
  }

  if (pastEvents === undefined || pastEvents.length === 0) {
    // Show nothing if there are no past events or if data is still loading
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
        {pastEvents.map((event) => (
          <EventCard
            key={event.id}
            event={event}
          />
        ))}
      </Grid>
    </>
  );
}
