import RequireEventPermission from 'components/RequireEventPermission';
import { useParams } from 'react-router';
import EventChallenges from './EventChallenges';
import NotAvailable from './NotAvailable';

export default function ChallengesTab() {
  const { idEvent } = useParams<{idEvent: string}>();
  const eventId = Number(idEvent);

  return (
    <RequireEventPermission
      permission="CAN_VIEW_CHALLENGES"
      eventId={eventId}
      permissionDeniedPlaceholder={<NotAvailable />}
    >
      <EventChallenges eventId={eventId} />
    </RequireEventPermission>
  );
}
