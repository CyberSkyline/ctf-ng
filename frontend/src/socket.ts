import { io } from 'socket.io-client';
import { mutate } from 'swr';
import { announce } from 'components/LiveAnnouncer';

const socket = io({ transports : [ 'websocket' ], upgrade : false });

// Trigger SWR revalidation when a "refetch" event is received from the server.
// The server sends the SWR key directly, unprefixed.
socket.on('refetch', (msg: {path: string}) => {
  mutate(msg.path);
});

// A system announcement also sends a generic notification just before it. Hold the "New notification"
// message briefly so the pair is announced once, as the more specific announcement.
const NOTIFICATION_ANNOUNCE_DELAY_MS = 750;
let pendingNotificationAnnouncement: ReturnType<typeof setTimeout> | undefined;

// Update notification hooks when a notification is received.
socket.on('notification', () => {
  mutate('/notifications/me');
  mutate('/notifications/me/unread-count');

  clearTimeout(pendingNotificationAnnouncement);
  pendingNotificationAnnouncement = setTimeout(() => announce('New notification'), NOTIFICATION_ANNOUNCE_DELAY_MS);
});

// Update announcements hook when an announcement is received.
socket.on('system_announcement', ({ title }: { title?: string } = {}) => {
  mutate('/announcements');

  clearTimeout(pendingNotificationAnnouncement);
  announce(title ? `New announcement: ${title}` : 'New announcement');
});

// Watch for image pull events and write them to the SWR cache as they occur.
// Global listeners make sure that events aren't missed if users navigate away and come back during a pull.
socket.on('pull-progress', ({ id, percent } : { id: string | number, percent: number }) => {
  mutate([ 'pull-status', id ], { status : 'pulling', percent }, false);
});

socket.on('pull-success', ({ id } : { id: string | number }) => {
  mutate([ 'pull-status', id ], { status : 'success' }, false);
});

socket.on('pull-fail', ({ id, error } : { id: string | number, error: string }) => {
  mutate([ 'pull-status', id ], { status : 'fail', error }, false);
});

export default socket;
