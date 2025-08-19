import useSWR, { mutate } from 'swr';
import { apiMutation } from '@/fetchers';
import type { Ticket, TicketMessage } from '@/types';

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
    (data): Ticket => data.id,
  ).finally(() => {
    mutate('/support/me/tickets');
  });
}

export function useMyTicketMessages(ticketId : number) {
  return useSWR<{
  ticket: Ticket,
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
