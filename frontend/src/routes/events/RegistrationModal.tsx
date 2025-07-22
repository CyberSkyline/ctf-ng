import {
  Em,
  Flex,
  Text,
  TextField,
} from '@radix-ui/themes';
import { useState } from 'react';
import Modal from 'components/Modal';
import { registerMyEvent } from '@/hooks/events';
import type { Event } from '@/types';

export default function RegistrationModal({ eventId }: {eventId : Event['id']}) {
  const [ leaderboardName, setLeaderboardName ] = useState<string>('');

  // Todo: alternate case when team game vs individual

  const register = () => {
    console.log('do registration');
    registerMyEvent(eventId);
  };

  return (
    <Modal
      title="Are you sure you want to register for this event?"
      buttonText="Register"
      onSubmit={register}
      onSubmitText="Register"
    >
      <Flex direction="column" gap="3">
        <Text><Em>Please do not use your real name.</Em></Text>
        <Text as="div" size="2" mb="1" weight="bold">
          Leaderboard Name:
        </Text>
        <TextField.Root
          placeholder="Enter your leaderboard name"
          value={leaderboardName}
          onChange={(e) => {
            setLeaderboardName(e.target.value);
          }}
        />
      </Flex>
    </Modal>
  );
}
