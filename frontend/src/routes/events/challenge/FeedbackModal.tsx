import { COLOR_INFO } from '@/constants';
import { submitChallengeFeedback, useMyChallengeFeedback } from '@/hooks/feedback';
import { Button, Text, TextArea } from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import FormField from 'components/FormField';
import Modal from 'components/Modal';
import { TbMessageCircle, TbMessageCircleCheck } from 'react-icons/tb';

/**
 * Character limit for textarea fields.
 * Should be safely below content length restriction assuming all text fields are at max.
 */
const CHAR_LIMIT = 500;

export default function FeedbackModal({ eventId, challengeId }: {eventId: number; challengeId: number}) {
  const { data : currentFeedback, error } = useMyChallengeFeedback(eventId, challengeId);

  const handleSubmit = async (
    data: {
      thoughts: string,
    },
  ) => submitChallengeFeedback(eventId, challengeId, data);

  return (
    <Modal
      title="Challenge Feedback"
      trigger={(
        <Button variant="ghost" color={COLOR_INFO} className="!m-0">
          {currentFeedback ? <TbMessageCircleCheck /> : <TbMessageCircle />}
          Feedback
        </Button>
      )}
      onSubmit={handleSubmit}
      submitVerb="Save"
      defaultValues={currentFeedback?.feedback_data || {}}
    >
      {({
        register, watch, formState : { errors },
      }) => (
        <>
          {error && (<ErrorCallout>{error.message}</ErrorCallout>)}
          <FormField
            label={`Briefly share your thoughts about this challenge. (e.g., difficulty,
             content, learning value, problem-solving, enjoyment, improvement areas.)`}
            rightComponent={(
              <Text size="2" color="gray" className="[label[data-invalid=true]+&]:!text-(--red-11)">
                {CHAR_LIMIT - watch('thoughts', '').length}
              </Text>
            )}
            error={errors.thoughts}
          >
            {(injected) => (
              <TextArea
                className="w-full"
                rows={5}
                {...register('thoughts', {
                  maxLength : { value : CHAR_LIMIT, message : `Feedback may not exceed ${CHAR_LIMIT} characters` },
                })}
                {...injected}
              />
            )}
          </FormField>
        </>
      )}
    </Modal>
  );
}
