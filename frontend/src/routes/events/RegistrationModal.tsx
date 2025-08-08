import { Button, TextField, RadioGroup } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { Form } from 'radix-ui';
import { useNavigate } from 'react-router';
import { useState } from 'react';
import type { Event } from '@/types';
import { registerMyEvent, registerMyEventTeamJoin } from '@/hooks/events';

export default function RegistrationModal({ eventId, isTeamGame }: {eventId : Event['id'], isTeamGame: boolean}) {
  const [ createTeam, setCreateTeam ] = useState(true);
  const navigate = useNavigate();

  const register = async (data: FormData) => {
    if (!createTeam) {
      const inviteCode = data.get('invite_code') as string;
      return registerMyEventTeamJoin(eventId, inviteCode).then(() => {
        navigate(`/events/${eventId}`);
      });
    }

    const leaderboardName = data.get('leaderboard_name') as string;
    return registerMyEvent(eventId, leaderboardName).then(() => {
      navigate(`/events/${eventId}`);
    });
  };

  return (
    <Modal
      title="Are you sure you want to register for this event?"
      description={isTeamGame ? 'Please do not use your real name or user name for your team name'
        : 'Please do not use your real name for your leaderboard name.'}
      trigger={(
        <Button variant="soft">Register</Button>
      )}
      onSubmit={register}
      submitVerb="Register"
      onOpenChange={() => setCreateTeam(true)}
    >
      {isTeamGame
        ? (
          <>
            <RadioGroup.Root
              value={createTeam ? 'new' : 'join'}
              onValueChange={(value) => {
                setCreateTeam(value === 'new');
              }}
              name="joinToggle"
            >
              <RadioGroup.Item value="new">Create New Team</RadioGroup.Item>
              <RadioGroup.Item value="join">Join Existing Team</RadioGroup.Item>
            </RadioGroup.Root>

            {createTeam ? (
              <Form.Field name="leaderboard_name">
                <Form.Label>
                  Team Name
                </Form.Label>
                <Form.Control asChild>
                  <TextField.Root
                    placeholder="Enter your team name"
                    required
                  />
                </Form.Control>
                <Form.Message match="valueMissing">
                  Please enter a leaderboard name.
                </Form.Message>
              </Form.Field>
            ) : (
              <Form.Field name="invite_code">
                <Form.Label>
                  Invite Code
                </Form.Label>
                <Form.Control asChild>
                  <TextField.Root
                    placeholder="Please enter the invite code"
                    required
                  />
                </Form.Control>
                <Form.Message match="valueMissing">
                  Please enter an invite code.
                </Form.Message>
              </Form.Field>
            )}

          </>
        ) : (
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
        )}
    </Modal>
  );
}
