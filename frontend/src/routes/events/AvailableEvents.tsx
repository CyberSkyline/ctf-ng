import {
  Button, Container, Flex, Heading, Text,
} from '@radix-ui/themes';
import EventHeader from 'components/EventHeader';
import HeaderContainer from 'components/HeaderContainer';
import { TbCheck } from 'react-icons/tb';

export default function AvailableEvents() {
  // Placeholder data
  const events = [ {
    id : 1,
    name : 'Event Name',
    description : 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
    dates : 'Jan 1, 2026 - Jan 4, 2026',
    maxTeamSize : 1,
    registered : false,
  }, {
    id : 2,
    name : 'Event Name 2',
    description : 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
    dates : 'Jan 1, 2026 - Jan 4, 2026',
    maxTeamSize : 5,
    registered : false,
  }, {
    id : 3,
    name : 'Event Name 3',
    description : 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
    dates : 'Jan 1, 2026 - Jan 4, 2026',
    maxTeamSize : 1,
    registered : true,
  } ];

  return (
    <>
      <HeaderContainer>
        <Heading size="9">Event Registration</Heading>
        <Text as="p" color="gray">Info about event registration.</Text>
      </HeaderContainer>
      <Container size="2">
        <Flex direction="column" gap="8" mt="8">
          {events.map((event) => (
            <EventHeader
              key={event.id}
              name={event.name}
              description={event.description}
              dateRange={event.dates}
              maxTeamSize={event.maxTeamSize}
            >
              <Button disabled={event.registered}>
                {event.registered && <TbCheck />}
                Register
                {event.registered && 'ed'}
              </Button>
            </EventHeader>
          ))}
        </Flex>
      </Container>
    </>
  );
}
