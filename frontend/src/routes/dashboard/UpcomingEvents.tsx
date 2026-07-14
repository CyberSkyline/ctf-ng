import { useMyEvents } from '@/hooks/events';
import { Link as RadixLink } from '@radix-ui/themes';
import { ErrorCallout, InfoCallout } from 'components/Callouts';
import EventGrid from 'components/EventGrid';
import { Link } from 'react-router';

export default function UpcomingEvents() {
  const { data, error, isLoading } = useMyEvents();
  const upcomingEvents = data?.filter((event) => !event.start_time || new Date() < new Date(event.start_time));

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
        You can browse and register for upcoming events on the
        {' '}
        <RadixLink asChild><Link to="/events">events page</Link></RadixLink>
        .
      </InfoCallout>
    );
  }

  return (
    <EventGrid loading={isLoading} events={upcomingEvents || []} />
  );
}
