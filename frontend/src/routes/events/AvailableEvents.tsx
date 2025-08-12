import {
  Button,
  Container,
  Flex,
  Heading,
  Text,
} from '@radix-ui/themes';
import EventHeader from 'components/EventHeader';
import HeaderContainer from 'components/HeaderContainer';
import { some } from 'lodash';
import { TbCheck } from 'react-icons/tb';
import { useEvents, useMyEvents } from '@/hooks/events';
import RegistrationModal from './RegistrationModal';

export default function AvailableEvents() {
  const { data : events } = useEvents();
  const { data : myRegisteredEvents } = useMyEvents();

  return (
    <>
      <HeaderContainer>
        <Heading size="9">Event Registration</Heading>
        <Text as="p" color="gray">Info about event registration.</Text>
      </HeaderContainer>
      {events && (
        <Container size="2">
          <Flex direction="column" gap="8" mt="8">
            {events?.map((event) => (
              <EventHeader
                key={event.id}
                event={event}
              >
                {
                  some(myRegisteredEvents, { id : event.id })
                    ? (
                      <Button disabled>
                        <TbCheck />
                        Registered
                      </Button>
                    )
                    : (
                      event.registration_open
                      && (
                        <RegistrationModal
                          eventId={event.id}
                          eventName={event.name}
                          isTeamGame={event.max_team_size > 1}
                        />
                      )
                    )
                }
              </EventHeader>
            ))}
          </Flex>
        </Container>
      )}
    </>
  );
}
