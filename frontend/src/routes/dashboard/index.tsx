import { Button, Container, Flex } from '@radix-ui/themes';
import PastEvents from 'components/dashboard/PastEvents';
import UpcomingEvents from 'components/dashboard/UpcomingEvents';
import EventHeader from 'components/event/EventHeader';
import HeaderContainer from 'components/HeaderContainer';

export default function Dashboard() {
  return (
    <>
      <HeaderContainer>
        { /* Events that are currently active or starting soon emphasized in the page header. */ }
        <EventHeader name="PC7 Teams Round 1" description="A brief description of what this event is." state="live">
          <Button variant="solid" size="2">Button 1</Button>
        </EventHeader>
      </HeaderContainer>

      <Container size="4">
        <Flex direction="column" gap="4" my="8">
          <UpcomingEvents events={[
            {
              id: 'pc7-track-a', name: 'PC7 Track A', color: 'red', description: 'A brief description of what this event is.',
            },
            {
              id: 'pc7-track-b', name: 'PC7 Track B', color: 'jade', description: 'A brief description of what this event is.',
            },
          ]}
          />

          <PastEvents events={[
            {
              id: 'pc6-team', name: 'PC6 Teams Round 1', color: 'lime', description: 'A brief description of what this event is.',
            },
            {
              id: 'pc5-track-a', name: 'PC5 Track A', color: 'red', description: 'A brief description of what this event is.',
            },
            {
              id: 'pc5-track-b', name: 'PC5 Track B', color: 'jade', description: 'A brief description of what this event is.',
            },
            {
              id: 'pc4-teams-finals', name: 'PC4 Teams Finals', color: 'orange', description: 'A brief description of what this event is.',
            },
            {
              id: 'pc4-track-a', name: 'PC4 Track A', color: 'plum', description: 'A brief description of what this event is.',
            },
            {
              id: 'pc4-track-b', name: 'PC4 Track B', color: 'blue', description: 'A brief description of what this event is.',
            },
            {
              id: 'pc3-teams', name: 'PC3 Teams', color: 'yellow', description: 'A brief description of what this event is.',
            },
          ]}
          />
        </Flex>
      </Container>
    </>
  );
}
