import { useMyEvents } from '@/hooks/events';
import { Grid, Link as RadixLink, Skeleton } from '@radix-ui/themes';
import { ErrorCallout, InfoCallout } from 'components/Callouts';
import { Link } from 'react-router';
import EventCard from './EventCard';

export default function UpcomingEvents() {
  const { data, error, isLoading } = useMyEvents();
  const upcomingEvents = data?.filter((event) => !event.start_time || new Date() < event.start_time);

  if (error) {
    return (
      <ErrorCallout>{error.message}</ErrorCallout>
    );
  }

  if (upcomingEvents !== undefined && upcomingEvents.length === 0) {
    return (
      <InfoCallout>
        You are not registered for any upcoming events.
        {' '}
        <RadixLink asChild><Link to="/events">Register for an upcoming event</Link></RadixLink>
        {' '}
        or head to the
        {' '}
        <RadixLink asChild><Link to="/practice">practice area</Link></RadixLink>
        {' '}
        to hone your skills!
      </InfoCallout>
    );
  }

  return (
    <Grid
      columns={{
        initial : '1', xs : '1', sm : '2', lg : '3',
      }}
      gap="4"
    >
      {isLoading && (
        <>
          <Skeleton className="min-h-48" />
          <Skeleton className="min-h-48" />
          <Skeleton className="min-h-48" />
        </>
      )}

      {upcomingEvents?.map((event) => (
        <EventCard
          key={event.id}
          event={event}
        />
      ))}
    </Grid>
  );
}
