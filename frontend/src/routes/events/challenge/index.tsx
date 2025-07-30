import {
  Card,
  Flex,
  Heading,
  Inset,
  Text,
} from '@radix-ui/themes';
import { useEffect, useState } from 'react';
import ChallengeSidebar from './ChallengeSidebar';

export default function Challenge() {
  const [ workspaceUp, setWorkspaceUp ] = useState(false);

  useEffect(() => {
    let timer = null;

    const checkWorkspace = async () => {
      const response = await fetch('/ng/vnc/access/vnc.html');
      if (response.ok) {
        setWorkspaceUp(true);
        clearInterval(timer!);
      }
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
              src="/ng/vnc/access/vnc.html?autoconnect=true&password=vncpassword&resize=remote&reconnect=true"
            />
          </Inset>
        ) : (
          <Flex
            direction="column"
            align="center"
            justify="center"
          >
            <Heading>Your workspace has not been started.</Heading>
            <Text>Press the connect button to start your workspace and connect it to this challenge.</Text>
          </Flex>
        )}
      </Card>

    </Flex>
  );
}
