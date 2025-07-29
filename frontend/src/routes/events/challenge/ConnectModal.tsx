import { connectWorkspace } from '@/hooks/challenge';
import { Button } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { useState } from 'react';
import { TbCheck, TbPlug } from 'react-icons/tb';

export default function ConnectModal({ eventId, challengeId }: {
  eventId: number;
  challengeId: number;
}) {
  const currentChallenge = null; // get from server once route is ready
  const [ loading, setLoading ] = useState(false);

  const handleConnect = async () => {
    setLoading(true);
    return connectWorkspace(eventId, challengeId).finally(() => {
      setLoading(false);
    });
  };

  if (currentChallenge === challengeId) {
    return (
      <Button variant="soft" disabled m="0" mt="3">
        <TbCheck />
        Workspace Connected
      </Button>
    );
  }

  if (currentChallenge === null) {
    // If the workspace isn't connected to anything, don't require confirmation
    return (
      <Button mt="3" onClick={handleConnect} loading={loading}>
        <TbPlug />
        Connect Workspace
      </Button>
    );
  }

  return (
    <Modal
      title="Switch challenge?"
      description="Your workspace will no longer be connected to (currently connected challenge)."
      trigger={(
        <Button mt="3" loading={loading}>
          <TbPlug />
          Connect Workspace
        </Button>
      )}
      onSubmit={handleConnect}
      submitVerb="Confirm"
    />
  );
}
