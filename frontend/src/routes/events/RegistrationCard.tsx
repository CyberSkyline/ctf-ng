import { useEventStatus, useMyEligibility } from '@/hooks/events';
import { useRegistration } from '@/hooks/users';
import type { Event } from '@/types';
import { Card, Flex, Text } from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import RequireEventPermission from 'components/RequireEventPermission';
import Statistic from 'components/Statistic';
import LeaveTeamModal from './LeaveTeamModal';
import RegistrationModal from './RegistrationModal';
import RenameTeamModal from './RenameTeamModal';

export default function RegistrationCard({ event }: {event: Event}) {
  const {
    isRegistered, isUnregistered, team, isLoading, error,
  } = useRegistration(event.id);
  const { isConcluded } = useEventStatus(event.id);

  const isIndividual = event.max_team_size === 1;

  // don't check eligibility if already registered since we know it will fail
  const { data : eligibility, error : eligibilityError } = useMyEligibility(isUnregistered ? event.id : null);

  if (isLoading) return null; // don't show anything while loading
  if (isUnregistered && !eligibility && !eligibilityError) return null; // if not eligible, don't show registration

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  if (isUnregistered && eligibilityError) {
    return <ErrorCallout>{eligibilityError.message}</ErrorCallout>;
  }

  return (
    <Card className="!flex flex-col gap-3">
      {isRegistered && (
        <>
          <Statistic
            label={`You ${isConcluded ? 'were' : 'are'} registered ${!isIndividual ? 'on team' : 'as'}:`}
            value={`${team!.name}`}
            size="6"
          />
          <Flex direction="row" gap="4" align="center" className="empty:!hidden">
            <RequireEventPermission eventId={event.id} permission="CAN_LEAVE_TEAM" permissionDeniedPlaceholder={null}>
              <LeaveTeamModal event={event} />
            </RequireEventPermission>
            <RequireEventPermission eventId={event.id} permission="CAN_EDIT_TEAM" permissionDeniedPlaceholder={null}>
              <RenameTeamModal event={event} />
            </RequireEventPermission>
          </Flex>
        </>
      )}
      { isUnregistered && eligibility && !eligibilityError && (
        <>
          <Text>You are not registered for this event.</Text>
          <Flex direction="row" gap="4" align="center">
            <RegistrationModal eventId={event.id} eventName={event.name} isTeamGame={event.max_team_size > 1} />
          </Flex>
        </>
      )}
    </Card>
  );
}
