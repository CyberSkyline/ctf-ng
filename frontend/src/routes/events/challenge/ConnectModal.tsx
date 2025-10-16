import { COLOR_POSITIVE, COLOR_WARNING } from '@/constants';
import { connectWorkspace, useCurrentChallengeId } from '@/hooks/container';
import { Button } from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import Modal from 'components/Modal';
import { useState } from 'react';
import { TbCheck, TbPlayerPlay } from 'react-icons/tb';

export default function ConnectModal({ challengeId }: {
  challengeId: number;
}) {
  const { data : currentChallenge, error } = useCurrentChallengeId();
  const [ loading, setLoading ] = useState(false);

  const handleConnect = async () => {
    setLoading(true);
    return connectWorkspace(challengeId).finally(() => {
      setLoading(false);
    });
  };

  if (error) {
    // if we can't get the current challenge, show an error where the button would otherwise go
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  if (currentChallenge === challengeId) {
    return (
      <Button variant="soft" disabled m="0">
        <TbCheck />
        Connected
      </Button>
    );
  }

  if (currentChallenge === null) {
    // If the workspace isn't connected to anything, don't require confirmation
    return (
      <Button onClick={handleConnect} loading={loading} color={COLOR_POSITIVE} className="pulsate">
        <TbPlayerPlay />
        Start Challenge
      </Button>
    );
  }

  return (
    <Modal
      title="Switch challenge?"
      description="Your workspace will be disconnected from your previous challenge and connected to this one."
      trigger={(
        <Button loading={loading} color={COLOR_POSITIVE} className="pulsate">
          <TbPlayerPlay />
          Start Challenge
        </Button>
      )}
      onSubmit={handleConnect}
      submitVerb="Confirm"
      submitColor={COLOR_WARNING}
    />
  );
}
