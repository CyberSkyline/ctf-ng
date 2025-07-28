import { registerMyEvent } from '@/hooks/events';
import type { Event } from '@/types';
import { Button, TextField } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { Form } from 'radix-ui';

export default function RegistrationModal({ eventId }: {eventId : Event['id']}) {
  // Todo: alternate case when team game vs individual

  const register = async (data: FormData) => {
    const leaderboardName = data.get('leaderboard_name') as string;
    return registerMyEvent(eventId, leaderboardName);
  };

  return (
    <Modal
      title="Are you sure you want to register for this event?"
      description="Please do not use your real name."
      trigger={(
        <Button variant="soft">Register</Button>
      )}
      onSubmit={register}
      submitVerb="Register"
    >
      <Form.Field name="leaderboard_name">
        <Form.Label>
          Leaderboard Name
        </Form.Label>
        <Form.Control asChild>
          <TextField.Root
            placeholder="Enter your leaderboard name"
            required
          />
        </Form.Control>
        <Form.Message match="valueMissing">
          Please enter a leaderboard name.
        </Form.Message>
      </Form.Field>
    </Modal>
  );
}
