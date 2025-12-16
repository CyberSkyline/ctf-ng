import { useMyChallengeFeedback } from '@/hooks/feedback';
import { useRegistration } from '@/hooks/users';
import { InfoCallout } from 'components/Callouts';

export default function FeedbackPrompt({ eventId, challengeId }: { eventId: number, challengeId: number }) {
  const { isFinished } = useRegistration(eventId);
  const { data } = useMyChallengeFeedback(isFinished ? eventId : null, challengeId);

  if (data !== null) return null;

  return (
    <InfoCallout>
      Please consider sharing your thoughts about this challenge by selecting the Feedback option above.
    </InfoCallout>
  );
}
