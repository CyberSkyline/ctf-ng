import { COLOR_INFO } from '@/constants';
import { submitChallengeFeedback, useMyChallengeFeedback } from '@/hooks/feedback';
import {
  Button,
  SegmentedControl,
  Text,
  TextArea,
} from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import FormField from 'components/FormField';
import Modal from 'components/Modal';
import { Controller } from 'react-hook-form';
import { TbMessageCircle, TbMessageCircleCheck } from 'react-icons/tb';

const items = Array(10).fill(null).map((_, i) => (
  // eslint-disable-next-line react/no-array-index-key
  <SegmentedControl.Item key={String(i)} value={String(i + 1)}>{i + 1}</SegmentedControl.Item>
));

/**
 * Character limit for textarea fields.
 * Should be safely below content length restriction assuming all text fields are at max.
 */
const CHAR_LIMIT = 500;

export default function FeedbackModal({ eventId, challengeId }: {eventId: number; challengeId: number}) {
  const { data : currentFeedback, error } = useMyChallengeFeedback(eventId, challengeId);

  const handleSubmit = async (
    data: {
      difficulty: number,
      quality: number,
      what_liked: string,
      how_to_improve: string
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
        register, control, watch, formState : { errors },
      }) => (
        <>
          {error && (<ErrorCallout>{error.message}</ErrorCallout>)}
          <FormField
            label="How would you rate the difficulty of this challenge on a 1-10 scale?"
            error={errors.difficulty}
          >
            {(injected) => (
              <Controller
                name="difficulty"
                control={control}
                rules={{ required : 'Please rate the difficulty' }}
                render={({ field }) => (
                  <SegmentedControl.Root
                    value={String(field.value)}
                    onValueChange={(v) => { field.onChange(Number(v)); }}
                    onBlur={field.onBlur}
                    ref={field.ref}
                    {...injected}
                  >
                    {items}
                  </SegmentedControl.Root>
                )}
              />
            )}
          </FormField>

          <FormField
            label="How would you rate the quality of this challenge on a 1-10 scale?"
            error={errors.quality}
          >
            {(injected) => (
              <Controller
                name="quality"
                control={control}
                rules={{ required : 'Please rate the quality' }}
                render={({ field }) => (
                  <SegmentedControl.Root
                    value={String(field.value)}
                    onValueChange={(v) => { field.onChange(Number(v)); }}
                    onBlur={field.onBlur}
                    ref={field.ref}
                    {...injected}
                  >
                    {items}
                  </SegmentedControl.Root>
                )}
              />
            )}
          </FormField>

          <FormField
            label="What did you like about this challenge?"
            rightComponent={(
              <Text size="2" color="gray" className="[label[data-invalid=true]+&]:!text-(--red-11)">
                {CHAR_LIMIT - watch('what_liked', '').length}
              </Text>
            )}
            error={errors.what_liked}
          >
            {(injected) => (
              <TextArea
                className="w-full"
                rows={5}
                {...register('what_liked', {
                  maxLength : { value : CHAR_LIMIT, message : `Feedback may not exceed ${CHAR_LIMIT} characters` },
                })}
                {...injected}
              />
            )}
          </FormField>
          <FormField
            label="How would you improve this challenge?"
            rightComponent={(
              <Text size="2" color="gray" className="[label[data-invalid=true]+&]:!text-(--red-11)">
                {CHAR_LIMIT - watch('how_to_improve', '').length}
              </Text>
            )}
            error={errors.how_to_improve}
          >
            {(injected) => (
              <TextArea
                className="w-full"
                rows={5}
                {...register('how_to_improve', {
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
