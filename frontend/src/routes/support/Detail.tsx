import { addNewTicketMessage, resolveMyTicket, useMyTicketMessages } from '@/hooks/support';
import { useCurrentUser } from '@/hooks/users';
import type { TicketAttachment } from '@/types';
import {
  Box,
  Button,
  Card,
  Container,
  Flex,
  Grid,
  Heading,
  Section,
  Separator,
  Text,
} from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import RichTextEditor from 'components/RichTextEditor';
import { StatusBadge } from 'components/StatusBadge';
import SupportAttachmentUpload from 'components/SupportAttachmentUpload';
import TicketMessagesCard from 'components/TicketMessagesCard';
import { isNil, isUndefined, map } from 'lodash';
import { useState } from 'react';
import { TbArrowLeft } from 'react-icons/tb';
import { useNavigate, useParams } from 'react-router';

export default function Detail() {
  const navigate = useNavigate();
  const { idTicket } = useParams();
  const { data, error : errorMessages, isLoading } = useMyTicketMessages(Number(idTicket));
  const { data : currentUser, error : errorUser, isLoading : isLoadingUser } = useCurrentUser();
  const [ version, setVersion ] = useState<number>(0); // To reinit the RichTextEditor
  const [ newText, setNewText ] = useState<string>('');
  const [ replyError, setReplyError ] = useState<string | null>(null);
  const [ resolveError, setResolveError ] = useState<boolean>(false);
  const [ resolveLoading, setResolveLoading ] = useState<boolean>(false);
  const [ replyLoading, setReplyLoading ] = useState<boolean>(false);

  if (isLoading || isLoadingUser) { return null; }

  if (isNil(currentUser) || errorUser) {
    return (
      <ErrorCallout>
        {isUndefined(errorUser)
          ? 'User could not be found'
          : errorUser.message}
      </ErrorCallout>
    );
  }

  if (isNil(data) || errorMessages) {
    return (
      <ErrorCallout>
        {isUndefined(errorMessages)
          ? 'The data for this ticket could not be found'
          : errorMessages.message}
      </ErrorCallout>
    );
  }

  const { messages, ticket, attachments } = data;

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
      <title>Support Ticket Detail</title>
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
          <TicketMessagesCard
            messages={messages}
            currentUserId={currentUser.id}
          />
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
              <StatusBadge status={status} />
            </Section>
            <Section size="1">
              Attachments
              <Separator size="4" />
              <SupportAttachmentUpload
                fileUploadPath={`/support/me/tickets/${idTicket}/upload`}
                ticketMutationUrl={`/support/me/tickets/${idTicket}`}
              />
              <br />
              <Grid columns="2" gap="1">
                {map(attachments, (attachment : TicketAttachment) => (
                  <img key={attachment.id} src={attachment.download_url} alt={attachment.filename} />
                ))}
              </Grid>
            </Section>
          </Flex>
        </Card>
      </Flex>
    </Container>
  );
}
