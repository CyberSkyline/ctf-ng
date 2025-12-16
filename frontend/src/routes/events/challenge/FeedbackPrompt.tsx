import { useMyChallengeFeedback } from '@/hooks/feedback';
import { useRegistration } from '@/hooks/users';
import { Strong } from '@radix-ui/themes';
import { InfoCallout } from 'components/Callouts';

export default function FeedbackPrompt({ eventId, challengeId }: { eventId: number, challengeId: number }) {
  const { isFinished } = useRegistration(eventId);
  const { data } = useMyChallengeFeedback(isFinished ? eventId : null, challengeId);

  if (data !== null) return null;

  return (
    <InfoCallout>
      <Strong>You are out of time.</Strong>
      {' '}
      Thank you for participating!
      Please consider sharing your thoughts about this challenge by selecting the Feedback option above.
    </InfoCallout>
  );
}
