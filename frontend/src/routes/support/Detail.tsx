import { useState } from 'react';
import {
  Box,
  Button,
  Card,
  Container,
  Flex,
  Heading,
  Separator,
  Text,
  Section,
} from '@radix-ui/themes';
import { StatusBadge } from 'components/StatusBadge';
import { ErrorCallout } from 'components/Callouts';
import { TbArrowLeft } from 'react-icons/tb';
import { useNavigate, useParams } from 'react-router';
import { isNil, isUndefined, map } from 'lodash';
import RichTextEditor from 'components/RichTextEditor';
import { useMyTicketMessages, addNewTicketMessage, resolveMyTicket } from '@/hooks/support';

export default function Detail() {
  const navigate = useNavigate();
  const { idTicket } = useParams();
  const { data, error : errorMessages } = useMyTicketMessages(Number(idTicket));
  const [ version, setVersion ] = useState<number>(0); // To reinit the RichTextEditor
  const [ newText, setNewText ] = useState<string>('');
  const [ replyError, setReplyError ] = useState<string | null>(null);
  const [ resolveError, setResolveError ] = useState<boolean>(false);
  const [ resolveLoading, setResolveLoading ] = useState<boolean>(false);
  const [ replyLoading, setReplyLoading ] = useState<boolean>(false);

  if (isNil(data) || errorMessages) {
    return (
      <ErrorCallout>
        {isUndefined(errorMessages)
          ? 'The data for this ticket could not be found'
          : errorMessages.message}
      </ErrorCallout>
    );
  }

  const { messages, ticket } = data;

  const {
    subject,
    status,
    event_name : eventName,
    team_name : teamName,
    challenge_name : challengeName,
  } = ticket;

  const resolveTicket = () => {
    setResolveLoading(true);
    setResolveError(false);

    resolveMyTicket(ticket.id)
      .catch((err) => setResolveError(err.message))
      .finally(() => setResolveLoading(false));
  };

  const sendNewMessage = async () => {
    setReplyError(null);
    setReplyLoading(true);

    // add a new message to the ticket
    addNewTicketMessage(ticket.id, newText)
      .catch((err) => setReplyError(err.message))
      .then(() => {
        setNewText('');
        setVersion((prev) => prev + 1); // This forces reMount of RichTextEditor
      }).finally(() => setReplyLoading(false));
  };

  return (
    <Container size="4">
      <Flex direction="row" gap="4">
        <Flex gap="3" direction="column" className="w-5/7">
          <Box maxWidth="200px">
            <Button
              variant="ghost"
              onClick={() => { navigate('/support'); }}
            >
              <TbArrowLeft />
              Support
            </Button>
          </Box>
          <Heading size="7">Ticket Detail</Heading>
          <Flex gap="2">
            <Heading size="3">Subject:</Heading>
            <Text>{subject}</Text>
          </Flex>
          <Box maxWidth="200px">
            <Button
              onClick={() => resolveTicket()}
              loading={resolveLoading}
              disabled={resolveLoading || status === 'closed'}
            >
              Mark Ticket as Resolved
            </Button>
            {resolveError && (
              <ErrorCallout>
                {resolveError}
              </ErrorCallout>
            )}
          </Box>
          <div>
            {map(messages, (message) => (
              <Card className="mt-2" key={message.id}>
                <Flex justify="between">
                  <Text weight="bold" size="2">{message.author_name}</Text>
                  <Text weight="bold" size="2">{new Date(message.created_at).toString()}</Text>
                </Flex>
                <Separator size="4" className="mb-1" />
                <Text as="p">
                  {message.text}
                </Text>
              </Card>
            ))}
          </div>
          <Flex gap="2" direction="column">
            <RichTextEditor
              initialValue={newText}
              onChange={setNewText}
              version={version}
            />
            <Button
              onClick={sendNewMessage}
              loading={replyLoading}
              disabled={replyLoading || status === 'closed'}
            >
              Reply
            </Button>
            {replyError && (
              <ErrorCallout>
                {replyError}
              </ErrorCallout>
            )}
          </Flex>
        </Flex>

        <Card size="3" className="w-2/7 h-fit">
          <Flex direction="column" gap="4">
            <Section size="1">
              Event
              <Separator size="4" />
              <Text>
                {isNil(eventName) ? 'N/A' : eventName}
              </Text>
            </Section>
            <Section size="1">
              Team
              <Separator size="4" />
              <Text>
                {isNil(teamName) ? 'N/A' : teamName}
              </Text>
            </Section>
            <Section size="1">
              Challenge
              <Separator size="4" />
              <Text>
                {isNil(challengeName) ? 'N/A' : challengeName}
              </Text>
            </Section>
            <Section size="1">
              Status
              <Separator size="4" />
              {StatusBadge(status)}
            </Section>
          </Flex>
        </Card>
      </Flex>
    </Container>
  );
}
