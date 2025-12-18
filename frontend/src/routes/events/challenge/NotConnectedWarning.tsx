import { useCurrentChallengeId } from '@/hooks/container';
import type { Challenge } from '@/types';
import { Strong } from '@radix-ui/themes';
import { WarningCallout } from 'components/Callouts';
import RequireEventPermission from 'components/RequireEventPermission';

export default function NotConnectedWarning({ challenge }: {challenge: Challenge}) {
  const {
    data : currentChallenge, isLoading,
  } = useCurrentChallengeId();

  if (!isLoading && currentChallenge !== challenge.id) {
    return (
      <RequireEventPermission eventId={challenge.event_id} permission="CAN_PLAY_CHALLENGES" permissionDeniedPlaceholder={null}>
        <WarningCallout>
          <Strong>You are not currently connected to this challenge.</Strong>
          {' '}
          Its resources will not be available in your workspace until you connect.
        </WarningCallout>
      </RequireEventPermission>
    );
  }

  return null;
}
