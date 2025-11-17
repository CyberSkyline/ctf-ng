import { COLOR_POSITIVE } from '@/constants';
import { startMyTeam, useEventStatus } from '@/hooks/events';
import type { Event } from '@/types';
import { Box, Button, Text } from '@radix-ui/themes';
import Modal from 'components/Modal';
import RequireEventPermission from 'components/RequireEventPermission';
import { TbPlayerPlay } from 'react-icons/tb';

export default function StartModal({ event }: {event: Event}) {
  const { isOngoing, isConcluded } = useEventStatus(event.id);
  const isIndividual = event.max_team_size === 1;

  const handleStart = async () => startMyTeam(event.id);

  let denyText = null;
  if (isOngoing) denyText = 'Waiting for your team captain to start the event.';
  if (isConcluded) denyText = 'This event has already concluded.';

  return (
    <RequireEventPermission
      eventId={event.id}
      permission="CAN_START_TEAM_TIMER"
      permissionDeniedPlaceholder={denyText
        ? (
          <Text size="3" color="gray">
            {denyText}
          </Text>
        )
        : null}
    >
      <Box>
        <Text size="3" color="gray">
          When
          {' '}
          {isIndividual ? 'you are' : 'your team is'}
          {' '}
          ready to start the event, press the start button below.
        </Text>
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
