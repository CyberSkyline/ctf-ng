import { io } from 'socket.io-client';
import { mutate } from 'swr';
import { APIPREFIX } from './constants';

const socket = io({ transports : [ 'websocket' ], upgrade : false });

// Trigger SWR revalidation when a "refetch" event is received from the server.
socket.on('refetch', (msg: {path: string}) => {
  // server refetch events use /ng prefix, we need to remove it here to match SWR keys
  const resourcePath = msg.path.replace(APIPREFIX, '');
  mutate(resourcePath);
});

// Update notification hooks when a notification is received.
socket.on('notification', () => {
  mutate('/notifications/me');
  mutate('/notifications/unread_count');
});

// Update announcements hook when an announcement is received.
socket.on('system_announcement', () => {
  mutate('/notifications/announcements');
});

export default socket;
