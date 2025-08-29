import {
  Badge,
  Box,
  Button,
  DataList,
  Flex,
  Select,
} from '@radix-ui/themes';
import AdminSidebar from 'components/AdminSidebar';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import {
  unassignTicket,
  assignTicket,
  closeTicket,
  muteTicket,
  putTicketEventTeam,
  removeTicketEventTeam,
  putTicketChallenge,
  removeTicketChallenge,
  useAdminTicketMessages,
  addNewAdminTicketMessage,
  useSupportTags,
  replaceTicketTags
} from '@/hooks/support';
import type { AdminTicket } from '@/types';
import { includes, isNil, isUndefined, map, without } from 'lodash';
import { useState } from 'react';
import RichTextEditor from 'components/RichTextEditor';
import { ErrorCallout } from 'components/Callouts';
import TicketMessagesCard from 'components/TicketMessagesCard';
import { useCurrentUser, useUserEvents } from '@/hooks/users';
import { useEventChallenges } from '@/hooks/challenge';
import { StatusBadge } from 'components/StatusBadge';
import {
  ChallengeIcon,
  EventIcon,
  TeamIcon,
  UserIcon,
} from '@/constants';
import Entity from 'components/Entity';
import { useSupportRoles } from '@/hooks/permissions';
import { TbX } from 'react-icons/tb';

export default function MessagesSidebar({ entity : selectedRow }: { selectedData: AdminTicket }) {
  // Dropdowns
  const [ actionError, setActionError ] = useState<string | null>(null)
  const [ actionLoading, setActionLoading ] = useState<boolean>(false);
  const [ assignedUser, setAssignedUser ] = useState<string>(String(selectedRow.assigned_to));
  const [ selectedEvent, setSelectedEvent ] = useState<string | undefined>(String(selectedRow.event_id))
  const [ selectedChallenge, setSelectedChallenge ] = useState<string | undefined>(String(selectedRow.challenge_id));
  const [ selectedTag, setSelectedTag ] = useState<string | undefined>('');

  // Rich Text Reply Messages
  const [ version, setVersion ] = useState<number>(0); // To reinit the RichTextEditor
  const [ newText, setNewText ] = useState<string>('');
  const [ replyError, setReplyError ] = useState<string | null>(null);
  const [ replyLoading, setReplyLoading ] = useState<boolean>(false);

  // Data fetchers
  const { data : currentUser } = useCurrentUser();
  const { data : assignableSupportUsers } = useSupportRoles();
  const { data: allTags } = useSupportTags();

  const { data, error } = useAdminTicketMessages(selectedRow.id);
  const { data: userEvents } = useUserEvents(data?.ticket.author_id);
  const { data: userChallenges } = useEventChallenges(data?.ticket.event_id);

  if (isNil(data) || error) {
    return (
      <ErrorCallout>
        {isUndefined(error)
          ? 'The data for this ticket could not be found'
          : error.message}
      </ErrorCallout>
    );
  }
  const { ticket, messages } = data;
  const { 
    id: ticketId,
    status,
    muted,
    subject,
    author_id,
    author_name,
    opened_timestamp,
    last_updated,
    event_id,
    event_name,
    team_id,
    team_name,
    challenge_id,
    challenge_name,
    closed_timestamp,
    tags,
  } = ticket;
  
  const sendNewMessage = () => {
    setReplyError(null);
    setReplyLoading(true);

    addNewAdminTicketMessage(ticket.id, newText)
      .catch((err) => setReplyError(err.message))
      .then(() => {
        setNewText('');
        setVersion((prev) => prev + 1); // This forces reMount of RichTextEditor
      }).finally(() => setReplyLoading(false));
  };

  const assign = (value: string) => {
    setAssignedUser(value)

    setActionLoading(true)
    setActionError(null);
    assignTicket(ticketId, Number(value))
      .catch((err) => setActionError(err.message))
      .finally(() => setActionLoading(false))
  }
  const unassign = () => {
    setAssignedUser('')

    setActionLoading(true)
    setActionError(null);
    unassignTicket(ticketId)
      .catch((err) => setActionError(err.message))
      .finally(() => setActionLoading(false))
  }

  const toggleClose = () => {
    setActionError(null);
    setActionLoading(true);
    closeTicket(ticketId, status === 'open')
      .catch((err) => setActionError(err.message))
      .finally(() => setActionLoading(false))
  }

  const toggleMute = () => {
    setActionError(null);
    setActionLoading(true)
    muteTicket(ticketId, !muted)
      .catch((err) => setActionError(err.message))
      .finally(() => setActionLoading(false))
  }

  const putEvent = (value: string) => {
    setSelectedEvent(value)

    setActionLoading(true);
    setActionError(null);

    putTicketEventTeam(ticketId, Number(value))
      .catch((err) => setActionError(err.message))
      .finally(() => setActionLoading(false))
  }
  const removeEvent = () => {
    setSelectedEvent('')
    setSelectedChallenge('');

    setActionLoading(true);
    setActionError(null);

    removeTicketEventTeam(ticketId)
      .catch((err) => setActionError(err.message))
      .finally(() => setActionLoading(false))
  }

  const putChallenge = (value: string) => {
    setSelectedChallenge(value)

    setActionLoading(true);
    setActionError(null);

    putTicketChallenge(ticketId, Number(value))
      .catch((err) => setActionError(err.message))
      .finally(() => setActionLoading(false))
  }
  const removeChallenge = () => {
    setSelectedChallenge('')

    setActionLoading(true);
    setActionError(null);

    removeTicketChallenge(ticketId)
      .catch((err) => setActionError(err.message))
      .finally(() => setActionLoading(false))
  }

  const updateTags = (id?: number) => {
    let newTags = map(tags, 'id');

    if(isUndefined(id)){
      //add tag
      if(!includes(newTags, id)){
        newTags.push(Number(selectedTag));
      }
    } else {
      //remove tag
      newTags = without(newTags, id)
    }

    replaceTicketTags(ticketId, newTags);
  }

  return (
    <AdminSidebar>
      <AdminSidebarHeader title="Ticket Details" />
      {actionError && <ErrorCallout>{actionError}</ErrorCallout>}
      <DataList.Root>
        <DataList.Item>
          <DataList.Label>Id</DataList.Label>
          <DataList.Value className='whitespace-pre-wrap'>
            {ticketId}
          </DataList.Value>
        </DataList.Item>
        <DataList.Item>
          <DataList.Label>Subject</DataList.Label>
          <DataList.Value className='whitespace-pre-wrap'>
            {subject}
          </DataList.Value>
        </DataList.Item>
        <DataList.Item>
          <DataList.Label>Status</DataList.Label>
          <DataList.Value className='whitespace-pre-wrap'>
            <Flex gap='2' direction='row' align='center'>
              <StatusBadge
                size='3'
                status={status}
              />
              <Button
                onClick={toggleClose}
                disabled={actionLoading}
                loading={actionLoading}
              >
                { status === 'open' ? 'Close' : 'Open' }
              </Button>
            </Flex>
          </DataList.Value>
        </DataList.Item>
        <DataList.Item>
          <DataList.Label>Author</DataList.Label>
          <DataList.Value className='whitespace-pre-wrap'>
            <Entity
              to={`/admin/users?id=${author_id}`}
              label={author_name}
              icon={UserIcon}
            />
          </DataList.Value>
        </DataList.Item>
        <DataList.Item>
          <DataList.Label>Assigned To</DataList.Label>
          <DataList.Value className='whitespace-pre-wrap'>
            <Flex gap='2' direction='row'>
              <Select.Root
                value={assignedUser}
                onValueChange={assign}
                disabled={actionLoading}
              >
                <Select.Trigger/>
                <Select.Content position='popper'>
                  {map(assignableSupportUsers, ({id, name}) => 
                    <Select.Item key={id} value={String(id)}>{name}</Select.Item>
                  )}
                </Select.Content>
              </Select.Root>
              <Button
                onClick={unassign}
                disabled={actionLoading || assignedUser === ''}
                loading={actionLoading}
              >
                Unassign
              </Button>
            </Flex>
          </DataList.Value>
        </DataList.Item>
        <DataList.Item>
          <DataList.Label>Tags</DataList.Label>
          <DataList.Value className='whitespace-pre-wrap'>
            <Flex gap='2' direction='row'>
              {map(tags, ({id, name, color}) => 
                <Button
                  key={id}
                  asChild
                  onClick={() => updateTags(id)}
                >
                  <Badge key={id}>
                    <Box
                      width='12px'
                      height='12px'
                      style={{backgroundColor: color}}
                    >
                    </Box>
                      {name}
                      <TbX/>
                  </Badge>
                </Button>
              )}
              <Select.Root
                value={selectedTag}
                onValueChange={setSelectedTag}
                disabled={actionLoading}
              >
                <Select.Trigger/>
                <Select.Content position='popper'>
                  {map(allTags, ({id, name, color}) => 
                    <Select.Item key={id} value={String(id)}>
                      <Flex gap='1' className='items-center'>
                        <Box
                          width='12px'
                          height='12px'
                          style={{backgroundColor: color}}
                        >
                        </Box>
                        {name}
                      </Flex>
                    </Select.Item>
                  )}
                </Select.Content>
              </Select.Root>
              <Button
                onClick={() => updateTags()}
                disabled={actionLoading || selectedTag === ''}
                loading={actionLoading}
              >
                Add Tag
              </Button>
            </Flex>
          </DataList.Value>
        </DataList.Item>
        <DataList.Item>
          <DataList.Label>Opened Date</DataList.Label>
          <DataList.Value className='whitespace-pre-wrap'>
            {opened_timestamp && opened_timestamp.toLocaleString()}
          </DataList.Value>
        </DataList.Item>
        <DataList.Item>
          <DataList.Label>Closed Date</DataList.Label>
          <DataList.Value className='whitespace-pre-wrap'>
            {closed_timestamp && closed_timestamp.toLocaleString()}
          </DataList.Value>
        </DataList.Item>
        <DataList.Item>
          <DataList.Label>Last Updated</DataList.Label>
          <DataList.Value className='whitespace-pre-wrap'>
            {last_updated && last_updated.toLocaleString()}
          </DataList.Value>
        </DataList.Item>
        <DataList.Item>
          <DataList.Label>Event</DataList.Label>
          <DataList.Value className='whitespace-pre-wrap'>
            <Flex gap='2' direction='row'>
              {event_id && event_name && <Entity
                to={`/admin/events?id=${event_id}`}
                label={event_name}
                icon={EventIcon}
              />}
              <Select.Root
                value={selectedEvent}
                onValueChange={putEvent}
                disabled={actionLoading}
              >
                <Select.Trigger/>
                <Select.Content position='popper'>
                  {map(userEvents, ({id, name}) => 
                    <Select.Item key={id} value={String(id)}>{name}</Select.Item>
                  )}
                </Select.Content>
              </Select.Root>
              <Button
                onClick={removeEvent}
                disabled={actionLoading || assignedUser === ''}
                loading={actionLoading}
              >
                Remove Event
              </Button>
            </Flex>
          </DataList.Value>
        </DataList.Item>
        <DataList.Item>
          <DataList.Label>Team</DataList.Label>
          <DataList.Value className='whitespace-pre-wrap'>
            {team_id && team_name && <Entity
              to={`/admin/teams?id=${team_id}`}
              label={team_name}
              icon={TeamIcon}
            />}
          </DataList.Value>
        </DataList.Item>
        <DataList.Item>
          <DataList.Label>Challenge</DataList.Label>
          <DataList.Value className='whitespace-pre-wrap'>
            <Flex gap='2' direction='row'>
              {challenge_id && challenge_name && <Entity
                to={`/admin/events?id=${event_id}`}
                label={challenge_name}
                icon={ChallengeIcon}
              />}
              {event_id && <>
                <Select.Root
                  value={selectedChallenge}
                  onValueChange={putChallenge}
                  disabled={actionLoading}
                >
                  <Select.Trigger/>
                  <Select.Content position='popper'>
                    {map(userChallenges, ({id, name}) => 
                      <Select.Item key={id} value={String(id)}>{name}</Select.Item>
                    )}
                  </Select.Content>
                </Select.Root>
                <Button
                  onClick={removeChallenge}
                  disabled={actionLoading || assignedUser === ''}
                  loading={actionLoading}
                >
                  Remove Challenge
                </Button>
              </>}
            </Flex>
          </DataList.Value>
        </DataList.Item>
        <DataList.Item>
          <DataList.Label>Muted</DataList.Label>
          <DataList.Value className='whitespace-pre-wrap'>
            <Button
              onClick={toggleMute}
              disabled={actionLoading}
              loading={actionLoading}
            >
              {muted ? 'Unmute' : 'Mute'}
            </Button>
          </DataList.Value>
        </DataList.Item>
      </DataList.Root>

      <AdminSidebarHeader title="Messages" />
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
          disabled={replyLoading}
        >
          Reply
        </Button>
        {replyError && (
          <ErrorCallout>
            {replyError}
          </ErrorCallout>
        )}
      </Flex>

    </AdminSidebar>
  );
}
