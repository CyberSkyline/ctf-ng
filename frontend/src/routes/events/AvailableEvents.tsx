import { useEvents } from '@/hooks/events';
import { Container, Heading } from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import EventGrid from 'components/EventGrid';
import HeaderContainer from 'components/HeaderContainer';

export default function AvailableEvents() {
  const { data : events, error, isLoading } = useEvents();

  return (
    <>
      <title>Events</title>
      <HeaderContainer>
        <Heading size="9">Events</Heading>
      </HeaderContainer>

      <Container size="4">
        {error && (<ErrorCallout className="mb-3">{error.message}</ErrorCallout>)}
        <EventGrid events={events || []} loading={isLoading} />
      </Container>
    </>
  );
}
