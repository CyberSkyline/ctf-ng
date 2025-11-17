import { useEvent } from '@/hooks/events';
import { useRegistration } from '@/hooks/users';
import { Container, Flex } from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import RequireEventPermission from 'components/RequireEventPermission';
import { useParams } from 'react-router';
import StartModal from 'routes/events/StartModal';
import EventChallenges from './EventChallenges';
import NotAvailable from './NotAvailable';

export default function ChallengesTab() {
  const { idEvent } = useParams<{idEvent: string}>();
  const eventId = Number(idEvent);
  const { data : event, error : eventError } = useEvent(eventId);
  const {
    isRegistered, isStarted,
  } = useRegistration(eventId);

  if (eventError) {
    return <ErrorCallout>{eventError.message}</ErrorCallout>;
  }

  return (
    <Flex direction="column">
      {isRegistered && (
        <>
          {/* Not available message */}
          <RequireEventPermission
            permission="CAN_VIEW_CHALLENGES"
            eventId={eventId}
            permissionDeniedPlaceholder={<NotAvailable />}
          />

          {/* Start button */}
          {!isStarted && event && (
            <Container size="2" className="text-center">
              <Flex direction="column" gap="3" align="center" mb="3">
                <StartModal event={event} />
              </Flex>
            </Container>
          )}

          {/* Challenge grid */}
          <RequireEventPermission
            permission="CAN_VIEW_CHALLENGES"
            eventId={eventId}
            permissionDeniedPlaceholder={null}
          >
            <EventChallenges eventId={eventId} />
          </RequireEventPermission>
        </>
      )}
    </Flex>
  );
}
