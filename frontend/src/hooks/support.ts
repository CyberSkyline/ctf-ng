import { apiMutation } from '@/fetchers';
import type {
  AdminTicket,
  Ticket,
  TicketAttachment,
  TicketMessage,
  TicketTag,
} from '@/types';
import useSWR, { mutate } from 'swr';

export function useMyTickets() {
  return useSWR<Ticket[], Error>('/support/me/tickets');
}

export function createTicket(formData: {
  subject: string,
  text: string,
  event_id?: number,
  challenge_id?: number
}) {
  return apiMutation('/support/tickets/create', formData, {
    method : 'POST',
  }).then(
    // This is for doing the navigation. Can only have one .then
    (data) => (data as Ticket).id,
  ).finally(() => {
    mutate('/support/me/tickets');
  });
}

export function useMyTicketMessages(ticketId : number) {
  return useSWR<{
    ticket: Ticket,
    attachments: TicketAttachment[],
    messages: TicketMessage[]
  }, Error>(
    ticketId ? `/support/me/tickets/${ticketId}` : null,
  );
}

export function addNewTicketMessage(ticketId: number, text: string) {
  return apiMutation(`/support/me/tickets/${ticketId}/add_message`, { text }, {
    method : 'POST',
  }).then(() => {
    mutate('/support/me/tickets');
    mutate(`/support/me/tickets/${ticketId}`);
  });
}

export function resolveMyTicket(ticketId: number) {
  return apiMutation(`/support/me/tickets/${ticketId}/close`, {}, {
    method : 'POST',
  }).then(() => {
    mutate('/support/me/tickets');
    mutate(`/support/me/tickets/${ticketId}`);
  });
}

/*
  ADMIN ROUTES
*/

export function useAdminAllTickets() {
  return useSWR<AdminTicket[], Error>('/admin/support/tickets');
}

/* Actions */
export function assignTicket(ticketId: number, userId: number) {
  return apiMutation(`/admin/support/tickets/${ticketId}/assign`, { user_id : userId }, {
    method : 'PUT',
  }).then(() => {
    mutate('/admin/support/tickets');
    mutate(`/admin/support/tickets/${ticketId}`);
  });
}
export function unassignTicket(ticketId: number) {
  return apiMutation(`/admin/support/tickets/${ticketId}/unassign`, { }, {
    method : 'PUT',
  }).then(() => {
    mutate('/admin/support/tickets');
    mutate(`/admin/support/tickets/${ticketId}`);
  });
}

export function closeTicket(ticketId: number, closed: boolean) {
  return apiMutation(`/admin/support/tickets/${ticketId}/close`, { closed }, {
    method : 'PUT',
  }).then(() => {
    mutate('/admin/support/tickets');
    mutate(`/admin/support/tickets/${ticketId}`);
  });
}

export function muteTicket(ticketId: number, muted: boolean) {
  return apiMutation(`/admin/support/tickets/${ticketId}/mute`, { muted }, {
    method : 'PUT',
  }).then(() => {
    mutate('/admin/support/tickets');
    mutate(`/admin/support/tickets/${ticketId}`);
  });
}

export function putTicketEventTeam(ticketId: number, eventId: number) {
  return apiMutation(`/admin/support/tickets/${ticketId}/event`, { event_id : eventId }, {
    method : 'PUT',
  }).then(() => {
    mutate('/admin/support/tickets');
    mutate(`/admin/support/tickets/${ticketId}`);
  });
}
export function removeTicketEventTeam(ticketId: number) {
  return apiMutation(`/admin/support/tickets/${ticketId}/event/remove`, { }, {
    method : 'PUT',
  }).then(() => {
    mutate('/admin/support/tickets');
    mutate(`/admin/support/tickets/${ticketId}`);
  });
}

export function putTicketChallenge(ticketId: number, challengeId: number) {
  return apiMutation(`/admin/support/tickets/${ticketId}/challenge`, { challenge_id : challengeId }, {
    method : 'PUT',
  }).then(() => {
    mutate('/admin/support/tickets');
    mutate(`/admin/support/tickets/${ticketId}`);
  });
}
export function removeTicketChallenge(ticketId: number) {
  return apiMutation(`/admin/support/tickets/${ticketId}/challenge/remove`, { }, {
    method : 'PUT',
  }).then(() => {
    mutate('/admin/support/tickets');
    mutate(`/admin/support/tickets/${ticketId}`);
  });
}

/* Ticket Messages */
export function useAdminTicketMessages(ticketId : number) {
  return useSWR<{
  ticket: AdminTicket,
  messages: TicketMessage[],
  attachments : TicketAttachment[],
}, Error>(
  ticketId ? `/admin/support/tickets/${ticketId}` : null,
);
}

export function addNewAdminTicketMessage(ticketId: number, text: string) {
  return apiMutation(`/admin/support/tickets/${ticketId}/add_message`, { text }, {
    method : 'POST',
  }).then(() => {
    mutate('/admin/support/tickets');
    mutate(`/admin/support/tickets/${ticketId}`);
  });
}

/* Ticket Tags */
export function replaceTicketTags(ticketId: number, data: number[]) {
  return apiMutation(`/admin/support/tickets/${ticketId}/tag`, { tag_ids : data }, {
    method : 'PUT',
  }).then(() => {
    mutate('/admin/support/tickets');
    mutate(`/admin/support/tickets/${ticketId}`);
  });
}

/* Admin Support Tags */
export function useSupportTags() {
  return useSWR<TicketTag[], Error>('/admin/support/tags');
}

export function createSupportTag(data: Omit<TicketTag, 'id' | 'ticket_count'>) {
  return apiMutation('/admin/support/tags', data, {
    method : 'POST',
  }).then(() => {
    mutate('/admin/support/tags');
  });
}

export function putSupportTag(tagId: number, data: Omit<TicketTag, 'id' | 'ticket_count'>) {
  return apiMutation(`/admin/support/tags/${tagId}`, data, {
    method : 'PUT',
  }).then(() => {
    mutate('/admin/support/tags');
  });
}
