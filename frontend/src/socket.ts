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

export default socket;
