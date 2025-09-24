import { COLOR_POSITIVE } from '@/constants';
import { startMyTeam, useMyTeam } from '@/hooks/events';
import type { Event } from '@/types';
import { Button } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbPlayerPlay } from 'react-icons/tb';

export default function StartModal({ event }: {event: Event}) {
  const { data : myTeam } = useMyTeam(event.id);
  const handleStart = async () => startMyTeam(event.id);

  if (!myTeam) return null;

  if (myTeam?.start_timestamp) {
    return (
      <Button disabled>
        <TbPlayerPlay />
        Started
      </Button>
    );
  }

  return (
    <Modal
      trigger={(
        <Button color={COLOR_POSITIVE} className="pulsate">
          <TbPlayerPlay />
          Start
        </Button>
      )}
      title="Start Event"
      description="Are you sure you want to start playing this event?"
      submitVerb="Start"
      submitColor={COLOR_POSITIVE}
      onSubmit={handleStart}
    />
  );
}
