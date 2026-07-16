import { useMyAnnouncements } from '@/hooks/announcements';
import { useMyEvents } from '@/hooks/events';

import { AnnouncementIcon, COLOR_WARNING } from '@/constants';
import {
  Callout,
  Container,
  Flex,
  Heading,
  Text,
} from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import HeaderContainer from 'components/HeaderContainer';
import { isEmpty, map } from 'lodash';
import PastEvents from 'routes/dashboard/PastEvents';
import UpcomingEvents from 'routes/dashboard/UpcomingEvents';
import EventCard from 'components/EventCard';

export default function Dashboard() {
  const { data, error } = useMyEvents();
  const { data : announcements, error : announcementError } = useMyAnnouncements();

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
      <title>Dashboard</title>
      {announcementError && <ErrorCallout className="mb-4">{announcementError.message}</ErrorCallout>}
      <HeaderContainer>
        {!isEmpty(announcements) && (
          <Flex direction="column" gap="1" className="mb-1">
            {
            map(announcements, ({ id, title, message }) => (
              <Callout.Root variant="surface" color={COLOR_WARNING} key={id}>
                <Callout.Icon>
                  <AnnouncementIcon aria-label="Warning" />
                </Callout.Icon>
                <Callout.Text className="whitespace-pre-wrap">
                  <Flex direction="column" className="-mt-[2px]">
                    <Text weight="bold" size="3">{title}</Text>
                    <Text>{message}</Text>
                  </Flex>
                </Callout.Text>
              </Callout.Root>
            ))
          }
          </Flex>
        )}
        {liveEvents && liveEvents.length > 0 && (
          <Flex direction="column" gap="3">
            {liveEvents.map((event) => (
              <EventCard key={event.id} event={event} />
            ))}
          </Flex>
        )}
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
