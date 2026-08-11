import { APIPREFIX } from '@/constants';
import { useBreakpoint } from '@/util';
import {
  Card,
  Flex,
  Heading,
  Inset,
  Spinner,
} from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import { useEffect, useState } from 'react';
import { Group, Panel, Separator } from 'react-resizable-panels';
import { twMerge } from 'tailwind-merge';
import ChallengeSidebar from './ChallengeSidebar';

export default function Challenge() {
  const [ workspaceUp, setWorkspaceUp ] = useState(false);
  const [ workspaceError, setWorkspaceError ] = useState(false);

  const isHorizontal = useBreakpoint('1280px');

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
    <Group orientation={isHorizontal ? 'horizontal' : 'vertical'} className="absolute inset-2 !flex-col-reverse xl:!flex-row">
      <Panel defaultSize="512px" minSize="512px" maxSize="50%">
        <ChallengeSidebar />
      </Panel>

      <Separator
        className={twMerge(
          'hover:bg-(--accent-6) focus:bg-(--accent-9) focus:outline-0 p-1 bg-clip-content box-content transition-colors',
          isHorizontal && 'w-0.5',
          !isHorizontal && 'h-0.5',
        )}
      />

      <Panel defaultSize="75%" minSize="50%">
        <Card
          className="grow basis-128 !flex flex-col items-stretch justify-center h-full"
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
      </Panel>
    </Group>
  );
}
