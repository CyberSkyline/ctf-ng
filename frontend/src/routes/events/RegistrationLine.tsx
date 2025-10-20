import { COLOR_POSITIVE } from '@/constants';
import { useEventStatus, useMyEligibility } from '@/hooks/events';
import { useRegistration } from '@/hooks/users';
import type { Event } from '@/types';
import { Text } from '@radix-ui/themes';
import { TbCheck } from 'react-icons/tb';
import RegistrationModal from './RegistrationModal';

export default function RegistrationLine({ event }: {event: Event}) {
  const {
    isRegistered, isUnregistered, isStarted, isFinished, team,
  } = useRegistration(event.id);
  const { isConcluded } = useEventStatus(event.id);

  // don't check eligibility if already registered since we know it will fail
  const { data : eligibility, error : eligibilityError } = useMyEligibility(isUnregistered ? event.id : null);

  if (isRegistered) {
    if (isFinished || isConcluded) {
      return (
        <Text color={COLOR_POSITIVE}>
          <TbCheck className="inline me-1" />
          You
          {event.max_team_size === 1 ? ' have ' : 'r team has '}
          completed this event.
        </Text>
      );
    }

    if (isStarted) {
      return (
        <Text color={COLOR_POSITIVE}>
          <TbCheck className="inline me-1" />
          You are currently playing.
          {team!.end_time
          && ` You${event.max_team_size > 1 ? 'r team' : ''} will finish at ${team!.end_time.toLocaleString()}.`}
        </Text>
      );
    }

    return (
      <Text color={COLOR_POSITIVE}>
        <TbCheck className="inline me-1" />
        You are registered
        {' '}
        {event.max_team_size > 1 ? 'on team' : 'as'}
        {' '}
        {team!.name}
      </Text>
    );
  }

  if (isUnregistered && eligibility && !eligibilityError) {
    return <RegistrationModal eventId={event.id} eventName={event.name} isTeamGame={event.max_team_size > 1} />;
  }

  return null;
}
