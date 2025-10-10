import { COLOR_POSITIVE } from '@/constants';
import { startMyTeam, useEvent } from '@/hooks/events';
import { useRegistration } from '@/hooks/users';
import { Box, Button, Text } from '@radix-ui/themes';
import Modal from 'components/Modal';
import RequireEventPermission from 'components/RequireEventPermission';
import { TbPlayerPlay } from 'react-icons/tb';

export default function StartModal({ eventId }: {eventId: number}) {
  const { isUnregistered, isFinished } = useRegistration(eventId);
  const { data : event } = useEvent(eventId);
  const isIndividual = (event?.max_team_size || 1) === 1;

  const handleStart = async () => startMyTeam(eventId);

  if (isUnregistered) return null;

  return (
    <RequireEventPermission
      eventId={eventId}
      permission="CAN_START_TEAM_TIMER"
      permissionDeniedPlaceholder={(
        <Text size="3" color="gray">
          {isFinished
            ? 'You have completed this event.'
            : 'Waiting for your team captain to start the event.'}
        </Text>
      )}
    >
      <Box>
        <Text size="3" color="gray">
          When
          {' '}
          {isIndividual ? 'you are' : 'your team is'}
          {' '}
          ready to start the event, press the start button below.
        </Text>
        {event?.time_limit_minutes && (
          <>
            <br />
            <Text color="gray" size="3">
              You will have
              {' '}
              {event?.time_limit_minutes || 'N/A'}
              {' '}
              minutes to complete as many challenges as possible.
            </Text>
          </>
        ) }
      </Box>
      <Modal
        trigger={(
          <Button color={COLOR_POSITIVE} className="pulsate">
            <TbPlayerPlay />
            Start Event
          </Button>
      )}
        title="Start Event"
        description="Are you sure you want to start this event?"
        submitVerb="Start"
        submitColor={COLOR_POSITIVE}
        onSubmit={handleStart}
      />
    </RequireEventPermission>
  );
}
