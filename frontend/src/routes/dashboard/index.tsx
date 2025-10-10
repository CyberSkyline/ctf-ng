import { useMyEvents } from '@/hooks/events';
import {
  Container,
  Flex,
  Heading,
  Skeleton,
} from '@radix-ui/themes';
import { ErrorCallout, InfoCallout } from 'components/Callouts';
import HeaderContainer from 'components/HeaderContainer';
import { isEmpty } from 'lodash';
import PastEvents from 'routes/dashboard/PastEvents';
import UpcomingEvents from 'routes/dashboard/UpcomingEvents';
import EventCard from './EventCard';

export default function Dashboard() {
  const { data, error, isLoading } = useMyEvents();

  const liveEvents = data?.filter(
    (event) => {
      if (event.start_time && new Date() < event.start_time) {
        // events that haven't started yet shouldn't be shown
        return false;
      }

      if (event.end_time && new Date() > event.end_time) {
        // events that have ended shouldn't be shown
        return false;
      }

      return true;
    },
  );

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  return (
    <>
      <HeaderContainer>
        {isEmpty(liveEvents) && (
          <Skeleton loading={isLoading}>
            <InfoCallout>
              No events are currently running. This should eventually be something more interesting, i.e. the first upcoming event or practice area.
            </InfoCallout>
          </Skeleton>
        )}
        <Flex direction="column" gap="3">
          {liveEvents?.map((event) => (
            <EventCard key={event.id} event={event} />
          ))}
        </Flex>
      </HeaderContainer>

      <Container size="4">
        <Flex direction="column" gap="4" my="8">
          <Heading size="6">Your Upcoming Events</Heading>
          <UpcomingEvents />

          <PastEvents />
        </Flex>
      </Container>
    </>
  );
}
