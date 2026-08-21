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

// Watch for image pull events and write them to the SWR cache as they occur.
// Global listeners make sure that events aren't missed if users navigate away and come back during a pull.
socket.on('pull-progress', ({ id, percent, host } : { id: string | number, percent: number, host: string }) => {
  mutate([ 'pull-status', id, host ], { status : 'pulling', percent }, false);
});

socket.on('pull-success', ({ id, host } : { id: string | number, host: string }) => {
  mutate([ 'pull-status', id, host ], { status : 'success' }, false);
});

socket.on('pull-fail', ({ id, error, host } : { id: string | number, error: string, host: string }) => {
  mutate([ 'pull-status', id, host ], { status : 'fail', error }, false);
});

export default socket;
