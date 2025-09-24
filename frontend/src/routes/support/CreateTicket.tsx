import {
  Box,
  Button,
  Container,
  Flex,
  Heading,
  TextField,
  Select,
} from '@radix-ui/themes';
import { TbArrowLeft } from 'react-icons/tb';
import { useNavigate } from 'react-router';
import RichTextEditor from 'components/RichTextEditor';
import { useState } from 'react';
import { Form } from 'radix-ui';
import { isEmpty, isUndefined, map } from 'lodash';
import { createTicket } from '@/hooks/support';
import { useMyEvents } from '@/hooks/events';
import { useMyChallenges } from '@/hooks/challenge';
import { ErrorCallout } from 'components/Callouts';

export default function CreateTicket() {
  const navigate = useNavigate();
  const [ error, setError ] = useState<string | null>(null);
  const [ loading, setLoading ] = useState<boolean>(false);
  const [ text, setText ] = useState<string>();
  const [ selectedEvent, setSelectedEvent ] = useState<string | undefined>();
  const [ selectedChallenge, setSelectedChallenge ] = useState<string | undefined>();

  const { data : events, error : eventsError } = useMyEvents();
  const { data : challenges, error : challengeError } = useMyChallenges(Number(selectedEvent));

  if (!isUndefined(eventsError)) {
    return <ErrorCallout>{eventsError?.message}</ErrorCallout>;
  } if (!isUndefined(challengeError)) {
    <ErrorCallout>{challengeError?.message}</ErrorCallout>;
  }

  const create = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);

    const formData = new FormData(e.currentTarget);
    const data = Object.fromEntries(formData.entries());
    const parsed = {
      subject : data?.subject as string,
      text : data?.text as string,
      event_id : data?.event_id ? Number(data.event_id) : undefined,
      challenge_id : data?.challenge_id ? Number(data.challenge_id) : undefined,
    };

    createTicket(parsed).then((ticketId) => {
      navigate(`/support/${ticketId}`);
    }).catch((err) => {
      setError(err.message);
    }).finally(() => {
      setLoading(false);
    });
  };

  return (
    <Container size="4">
      <Flex gap="3" direction="column">
        <Box maxWidth="200px">
          <Button
            variant="ghost"
            onClick={() => { navigate('/support'); }}
          >
            <TbArrowLeft />
            Support
          </Button>
        </Box>
        <Heading size="7">Create a New Support Ticket</Heading>

        <Form.Root onSubmit={create}>
          <Form.Field name="subject">
            <Form.Label>Subject: *</Form.Label>
            <Form.Control asChild>
              <TextField.Root
                placeholder="Enter a subject for your ticket"
                required
              />
            </Form.Control>
            <Form.Message match="valueMissing">
              Subject is a required field
            </Form.Message>
          </Form.Field>

          <Form.Field name="text">
            <Form.Label>Message: *</Form.Label>
            {/* Hidden input to track value and error handling */}
            <Form.Control asChild>
              <input
                type="hidden"
                name="text"
                value={text}
                required
              />
            </Form.Control>
            {/* Displayed editor */}
            <RichTextEditor
              initialValue={text}
              onChange={setText}
            />
            {text === '' && (
              <Form.Message>
                Message is a required field.
              </Form.Message>
            )}
          </Form.Field>

          <Form.Field name="event_id" className="mt-2">
            <Form.Label className="mr-2">Event:</Form.Label>
            <Select.Root
              name="event_id"
              value={selectedEvent}
              onValueChange={(v: string) => setSelectedEvent(v)}
            >
              <Select.Trigger placeholder="Select an event" className="w-[200px]" />
              <Select.Content>
                <Select.Group>
                  {map(events, (event) => (
                    <Select.Item
                      key={event.id}
                      value={String(event.id)}
                    >
                      {event.name}
                    </Select.Item>
                  ))}
                </Select.Group>
              </Select.Content>
            </Select.Root>
          </Form.Field>

          {!isEmpty(selectedEvent)
            && (
              <Form.Field name="challenge_id" className="mt-2">
                <Form.Label className="mr-2">Challenge:</Form.Label>
                <Select.Root
                  name="challenge_id"
                  value={selectedChallenge}
                  onValueChange={(v: string) => setSelectedChallenge(v)}
                >
                  <Select.Trigger placeholder="Select a challenge" />
                  <Select.Content>
                    <Select.Group>
                      {map(challenges, (challenge) => (
                        <Select.Item
                          key={challenge.challenge_id}
                          value={String(challenge.challenge_id)}
                        >
                          {challenge.challenge_name}
                        </Select.Item>
                      ))}
                    </Select.Group>
                  </Select.Content>
                </Select.Root>
              </Form.Field>
            )}

          {error && <ErrorCallout className="mt-2">{error}</ErrorCallout>}

          <Form.Submit asChild>
            <Button
              type="submit"
              className="!mt-2"
              loading={loading}
              disabled={loading}
            >
              Submit Ticket
            </Button>
          </Form.Submit>
        </Form.Root>
      </Flex>
    </Container>
  );
}
