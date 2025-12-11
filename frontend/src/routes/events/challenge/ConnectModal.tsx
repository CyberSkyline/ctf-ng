import { COLOR_NEGATIVE, COLOR_POSITIVE, COLOR_WARNING } from '@/constants';
import { connectWorkspace, recycleChallengeContainers, useCurrentChallengeId } from '@/hooks/container';
import { Button, Flex } from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import Modal from 'components/Modal';
import { useState } from 'react';
import { TbCheck, TbPlayerPlay, TbRotateClockwise } from 'react-icons/tb';

export default function ConnectModal({
  eventId, challengeId, isTeam, onError,
}: {
  eventId: number;
  challengeId: number;
  isTeam: boolean;
  onError?: (error: Error | undefined) => void;
}) {
  const {
    data : currentChallenge, isValidating, error,
  } = useCurrentChallengeId();
  const [ loading, setLoading ] = useState(false);

  const handleConnect = async () => {
    setLoading(true);
    onError?.(undefined);
    return connectWorkspace(eventId, challengeId).finally(() => {
      setLoading(false);
    });
  };

  const handleReset = async () => {
    onError?.(undefined);
    return recycleChallengeContainers(eventId, challengeId);
  };

  if (error) {
    // if we can't get the current challenge, show an error where the button would otherwise go
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  if (currentChallenge === challengeId) {
    return (
      <Flex gap="1" align="center">
        <Button variant="soft" disabled m="0">
          <TbCheck />
          Connected
        </Button>
        <Modal
          title="Reset challenge?"
          description={`The challenge will be reset to its initial state${isTeam ? ' for all players on your team' : ''}.`}
          trigger={(
            <Button variant="ghost" className="!m-0" color={COLOR_NEGATIVE} aria-label="Reset Challenge">
              <TbRotateClockwise />
              Reset
            </Button>
          )}
          submitVerb="Reset"
          submitColor={COLOR_NEGATIVE}
          onSubmit={handleReset}
        />
      </Flex>
    );
  }

  if (currentChallenge === null) {
    // If the workspace isn't connected to anything, don't require confirmation
    return (
      <Button
        // For starting without modal, pass errors to the parent for display
        onClick={
            () => handleConnect()
              .catch(onError)
        }
        loading={loading || isValidating}
        color={COLOR_POSITIVE}
        className="pulsate"
      >
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
        <Button loading={loading || isValidating} color={COLOR_POSITIVE} className="pulsate">
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
