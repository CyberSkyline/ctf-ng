import { useMyEvents } from '@/hooks/events';
import { Heading } from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import EventGrid from 'components/EventGrid';

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
      <EventGrid events={pastEvents || []} group />
    </>
  );
}
