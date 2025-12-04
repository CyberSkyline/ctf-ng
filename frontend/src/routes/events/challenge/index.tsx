import { APIPREFIX } from '@/constants';
import {
  Card,
  Flex,
  Heading,
  Inset,
  Spinner,
} from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import { useEffect, useState } from 'react';
import ChallengeSidebar from './ChallengeSidebar';

export default function Challenge() {
  const [ workspaceUp, setWorkspaceUp ] = useState(false);
  const [ workspaceError, setWorkspaceError ] = useState(false);

  // Polling logic to gracefully wait for the workspace to be ready.
  // NoVNC will give up instantly if the workspace isn't ready yet, so we need to
  // check first before rendering the iframe
  useEffect(() => {
    let timer = null;
    let attempts = 0;

    const checkWorkspace = () => {
      if (attempts >= 6) {
        // Once we've made 6 attempts (30 seconds), give up and show error
        clearInterval(timer!);
        setWorkspaceError(true);
      }

      // Try to connect to the websockify instance running in the workspace container.
      const socket = new WebSocket(`${APIPREFIX}/vnc/access/websockify`);
      attempts += 1;

      // If the socket opens, the workspace is up - close our socket and start NoVNC.
      socket.onopen = () => {
        setWorkspaceUp(true);
        clearInterval(timer!);
        socket.close();
      };
    };

    timer = setInterval(checkWorkspace, 5000);
    checkWorkspace();

    return () => clearInterval(timer);
  }, []);

  return (
    <Flex
      direction={{ initial : 'column-reverse', md : 'row' }}
      gap="2"
      position={{
        md : 'absolute',
      }}
      inset="2"
    >
      <ChallengeSidebar />

      <Card
        className="grow basis-128 !flex flex-col items-stretch justify-center"
      >
        {workspaceUp ? (
          <Inset
            side="all"
            className="grow shrink"
          >
            <iframe
              title="VNC session"
              className="w-full h-full"
              src={`${PUBLIC_BASE}/novnc/vnc.html?autoconnect=true&path=${APIPREFIX}/vnc/access/websockify&resize=remote&reconnect=true`}
            />
          </Inset>
        ) : (
          <Flex
            direction="column"
            align="center"
            justify="center"
          >
            {workspaceError
              ? (<ErrorCallout>Unable to connect to your workspace. Please try reloading the page, or contact support if the issue persists.</ErrorCallout>)
              : (
                <>
                  <Heading>Connecting to workspace...</Heading>
                  <Spinner className="mt-4" />
                </>
              )}
          </Flex>
        )}
      </Card>

    </Flex>
  );
}
