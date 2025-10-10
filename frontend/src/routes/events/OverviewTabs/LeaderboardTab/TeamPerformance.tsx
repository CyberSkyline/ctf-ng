import { useMyTeamScore } from '@/hooks/scoring';
import { useRegistration } from '@/hooks/users';
import { Flex } from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import Statistic from 'components/Statistic';

export default function TeamPerformance({ eventId }: {eventId: number}) {
  const { isRegistered, error } = useRegistration(eventId);

  // don't fetch score if not registered since we know it will fail
  const { data : score, error : scoreError } = useMyTeamScore(isRegistered ? eventId : null);

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  if (isRegistered) {
    return (
      <>
        {scoreError && <ErrorCallout>{scoreError.message}</ErrorCallout>}
        <Flex direction="row" gap="3">
          <Statistic value={score?.points ?? ''} label="Your Score" description={`Last updated ${score?.last_update.toLocaleString()}`} />
        </Flex>
      </>
    );
  }
}
