import { useMyEvents } from '@/hooks/events';
import { Button, Container, Flex } from '@radix-ui/themes';
import { ErrorCallout, InfoCallout } from 'components/Callouts';
import EventHeader from 'components/EventHeader';
import HeaderContainer from 'components/HeaderContainer';
import { Link } from 'react-router';
import PastEvents from 'routes/dashboard/PastEvents';
import UpcomingEvents from 'routes/dashboard/UpcomingEvents';

export default function Dashboard() {
  const { data, error } = useMyEvents();

  // Split registered events into past, present, and future
  const upcomingEvents = data?.filter((event) => !event.start_time || new Date() < event.start_time) || [];
  const pastEvents = data?.filter((event) => event.end_time && new Date() > event.end_time) || [];
  const liveEvents = data?.filter(
    (event) => event.start_time && event.end_time && new Date() >= event.start_time && new Date() <= event.end_time,
  ) || [];

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  return (
    <>
      <HeaderContainer>
        {liveEvents.length === 0 && (
          <InfoCallout>
            No events are currently running. This should eventually be something more interesting, i.e. the first upcoming event or practice area.
          </InfoCallout>
        )}
        {liveEvents.map((event) => (
          <EventHeader
            key={event.id}
            event={event}
          >
            <Button asChild>
              <Link to={`/events/${event.id}`}>
                Go
              </Link>
            </Button>
          </EventHeader>
        ))}
      </HeaderContainer>

      <Container size="4">
        <Flex direction="column" gap="4" my="8">
          <UpcomingEvents events={upcomingEvents} />

          <PastEvents events={pastEvents} />
        </Flex>
      </Container>
    </>
  );
}
