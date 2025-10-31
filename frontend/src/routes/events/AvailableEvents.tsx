import { useEvents } from '@/hooks/events';
import { Container, Heading } from '@radix-ui/themes';
import EventGrid from 'components/EventGrid';
import HeaderContainer from 'components/HeaderContainer';

export default function AvailableEvents() {
  const { data : events, isLoading } = useEvents();

  return (
    <>
      <title>Events</title>
      <HeaderContainer>
        <Heading size="9">Events</Heading>
      </HeaderContainer>
      {events && (
        <Container size="4">
          <EventGrid events={events} loading={isLoading} />
        </Container>
      )}
    </>
  );
}
