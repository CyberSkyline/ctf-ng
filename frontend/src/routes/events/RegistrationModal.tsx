import {
  Button,
  Checkbox,
  TextField,
  Text,
  Flex,
} from '@radix-ui/themes';
import Modal from 'components/Modal';
import { Form } from 'radix-ui';
import { useNavigate, useParams } from 'react-router';
import { useState } from 'react';
import { isUndefined } from 'lodash';
import type { Event } from '@/types';
import { registerMyEvent, registerMyEventTeamJoin } from '@/hooks/events';

export default function RegistrationModal({ eventId, eventName, isTeamGame }: {eventId : Event['id'], eventName: string, isTeamGame: boolean}) {
  const [ checked, setChecked ] = useState(false);
  const { inviteCode, idEvent } = useParams();
  const joinWithCode = !!(eventId === Number(idEvent) && !isUndefined(inviteCode));

  const navigate = useNavigate();

  const register = async (data: FormData) => {
    if (joinWithCode) {
      return registerMyEventTeamJoin(eventId, inviteCode).then(() => {
        navigate(`/events/${eventId}`);
      });
    }

    const leaderboardName = data.get('leaderboard_name') as string;
    return registerMyEvent(eventId, leaderboardName).then(() => {
      navigate(`/events/${eventId}`);
    });
  };

  function getDescription() {
    if (joinWithCode) {
      return undefined;
    }
    return isTeamGame ? 'Please do not use your real name or user name for your team name'
      : 'Please do not use your real name for your leaderboard name.';
  }

  return (
    <Modal
      title="Are you sure you want to register for this event?"
      description={getDescription()}
      trigger={(
        <Button variant="soft">Register</Button>
      )}
      onSubmit={register}
      submitVerb="Register"
      onOpenChange={() => {
        setChecked(false);
      }}
      defaultOpen={joinWithCode}
    >
      {
        joinWithCode ? (
          <Flex gap="2">
            <Text as="label" className="font-bold">Event Name: </Text>
            <Text as="label">{eventName}</Text>
          </Flex>
        ) : (
          <Form.Field name="leaderboard_name">
            <Form.Label>
              {isTeamGame ? 'Team Name' : 'Leaderboard Name'}
            </Form.Label>
            <Form.Control asChild>
              <TextField.Root
                placeholder={isTeamGame ? 'Enter your team name' : 'Enter your leaderboard name'}
                required
              />
            </Form.Control>
            <Form.Message match="valueMissing">
              Please enter a name.
            </Form.Message>
          </Form.Field>
        )
      }

      <Form.Field name="terms_conditions">
        <Form.Label asChild>
          <Text as="label" size="2">
            <Flex as="span" gap="2">
              <Checkbox
                checked={checked}
                onCheckedChange={(val) => setChecked(val === true)}
              />
              Agree to the Terms and Conditions
            </Flex>
          </Text>
        </Form.Label>
        {/* Hidden native checkbox for validation */}
        <Form.Control asChild>
          <input
            type="checkbox"
            checked={checked}
            onChange={(e) => setChecked(e.target.checked)}
            required
            className="hidden"
          />
        </Form.Control>

        <Form.Message match="valueMissing">
          You must accept the terms and conditions.
        </Form.Message>
      </Form.Field>
    </Modal>
  );
}
