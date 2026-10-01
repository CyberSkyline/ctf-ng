import { COLOR_POSITIVE } from '@/constants';
import { submitEventFeedback, useMyEventFeedback } from '@/hooks/feedback';
import {
  Button,
  Container,
  Flex,
  RadioCards,
  SegmentedControl,
  Strong,
  Text,
  TextArea,
} from '@radix-ui/themes';
import { ErrorCallout, InfoCallout, SuccessCallout } from 'components/Callouts';
import FormField from 'components/FormField';
import { useEffect, useState } from 'react';
import { Controller, useForm } from 'react-hook-form';
import { TbCheck, TbSend } from 'react-icons/tb';
import { useParams } from 'react-router';

type EventFeedbackFormData = Partial<{
  role: string,
  cyber_experience: string,
  participation_reason: string,
  participation_again: string,
  difficulty_rating: string,
  relevancy_rating: string,
  engagement_rating: string,
  thoughts: string,
  additional_feedback: string,
  additional_topics: string,
}>

const ROLES = [
  'Incident Response',
  'Digital Forensics',
  'Network Operations',
  'Defensive Cybersecurity',
  'Exploitation Analysis',
  'Cyberspace Operations',
  'Secure Software Development',
  'Vulnerability Analysis',
  'Data Analysis',
  'Threat Analysis',
];

const EXPERIENCE_LEVELS = [
  '1-5 years',
  '5-10 years',
  '10-15 years',
  '15+ years',
  'I have no experience in this role',
];

const PARTICIPATION_REASONS: Record<string, string> = {
  'Promotional messages about the President\'s Cup' : 'Emails, social media, presentation, etc',
  'Word-of-Mouth' : 'A supervisor, colleague or friend encouraged me to register',
  'Returning Participant' : 'Enjoyed the event and wanted to participate in it again',
};

const scale = Array(10).fill(null).map((_, i) => (
  // eslint-disable-next-line react/no-array-index-key
  <SegmentedControl.Item key={String(i)} value={String(i + 1)}>{i + 1}</SegmentedControl.Item>
));

const CHAR_LIMIT = 500;

export default function FeedbackTab() {
  const { idEvent } = useParams<{idEvent: string}>();
  const eventId = Number(idEvent);
  const { data : currentFeedback, error : currentFeedbackError } = useMyEventFeedback(eventId);

  const {
    register, reset, control, watch, handleSubmit, formState : { errors },
  } = useForm<EventFeedbackFormData>({
    mode : 'onTouched',
    defaultValues : currentFeedback?.feedback_data || {},
  });

  const [ buttonState, setButtonState ] = useState<null | 'loading' | 'success'>(null);
  const [ error, setError ] = useState<string | null>(null);

  const submitFeedback = async (data: EventFeedbackFormData) => {
    setButtonState('loading');
    setError(null);
    try {
      await submitEventFeedback(eventId, data);
      setButtonState('success');
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setTimeout(() => {
        setButtonState(null);
      }, 2000);
    }
  };

  useEffect(() => {
    // apply current feedback data to form when loaded
    reset(currentFeedback?.feedback_data || {});
  }, [ currentFeedback, reset ]);

  return (
    <Container size="4">
      {currentFeedbackError && (<ErrorCallout className="mb-3">{currentFeedbackError.message}</ErrorCallout>)}
      {error && (<ErrorCallout className="mb-3">{error}</ErrorCallout>)}

      {currentFeedback && (
        <SuccessCallout className="mb-3">
          <Strong>Thank you for your feedback!</Strong>
          {' '}
          You may update the form and resubmit below if you would like to make changes.
        </SuccessCallout>
      )}
      <form onSubmit={(e) => {
        handleSubmit(submitFeedback)(e);
      }}
      >
        <Flex direction="column" gap="3">
          <FormField
            label={`Which of the following NICE Work Roles best aligns with your current position? 
              (If you're unsure, choose the closest match or select "Other")`}
            error={errors.role}
          >
            {(injected) => (
              <Controller
                name="role"
                control={control}
                rules={{ maxLength : { value : CHAR_LIMIT, message : `Feedback cannot exceed ${CHAR_LIMIT} characters.` } }}
                render={({ field }) => (
                  <RadioCards.Root
                    value={field.value || null}
                    onValueChange={field.onChange}
                    onBlur={field.onBlur}
                    columns="3"
                    gap="1"
                    {...injected}
                  >
                    {ROLES.map((role) => (
                      <RadioCards.Item key={role} value={role}>
                        {role}
                      </RadioCards.Item>
                    ))}

                    <TextArea
                      value={field.value && ROLES.includes(field.value) ? '' : field.value || ''}
                      onChange={field.onChange}
                      onBlur={field.onBlur}
                      placeholder="Other..."
                      className="!min-h-min"
                      rows={1}
                    />
                  </RadioCards.Root>
                )}
              />
            )}
          </FormField>

          <FormField
            label="How many years of experience do you have in the NICE Work Role you selected above?"
            error={errors.cyber_experience}
          >
            {(injected) => (
              <Controller
                name="cyber_experience"
                control={control}
                render={({ field }) => (
                  <RadioCards.Root
                    value={field.value || null}
                    onValueChange={field.onChange}
                    columns="3"
                    gap="1"
                    {...injected}
                  >
                    {EXPERIENCE_LEVELS.map((level) => (
                      <RadioCards.Item key={level} value={level}>
                        {level}
                      </RadioCards.Item>
                    ))}
                  </RadioCards.Root>
                )}
              />
            )}
          </FormField>

          <FormField
            label={`What motivated you to participate in the President's Cup?`}
            error={errors.participation_reason}
          >
            {(injected) => (
              <Controller
                name="participation_reason"
                control={control}
                rules={{ maxLength : { value : CHAR_LIMIT, message : `Feedback cannot exceed ${CHAR_LIMIT} characters.` } }}
                render={({ field }) => (
                  <RadioCards.Root
                    value={field.value || null}
                    onValueChange={field.onChange}
                    onBlur={field.onBlur}
                    columns="2"
                    gap="1"
                    className="[&_button]:!flex-col"
                    {...injected}
                  >
                    {Object.entries(PARTICIPATION_REASONS).map(([ key, description ]) => (
                      <RadioCards.Item key={key} value={key}>
                        <Strong>{key}</Strong>
                        {description}
                      </RadioCards.Item>
                    ))}

                    <TextArea
                      value={field.value && Object.keys(PARTICIPATION_REASONS).includes(field.value) ? '' : field.value || ''}
                      onChange={field.onChange}
                      onBlur={field.onBlur}
                      placeholder="Other..."
                      className="!min-h-min"
                      rows={3}
                    />
                  </RadioCards.Root>
                )}
              />
            )}
          </FormField>

          <FormField
            label="Will you participate again next year if your schedule permits?"
            error={errors.participation_again}
          >
            {(injected) => (
              <Controller
                name="participation_again"
                control={control}
                render={({ field }) => (
                  <RadioCards.Root
                    value={field.value || null}
                    onValueChange={field.onChange}
                    columns="3"
                    gap="1"
                    {...injected}
                  >
                    <RadioCards.Item value="Yes">
                      Yes
                    </RadioCards.Item>
                    <RadioCards.Item value="No">
                      No
                    </RadioCards.Item>
                    <RadioCards.Item value="Unsure">
                      {`I'm unsure at this time`}
                    </RadioCards.Item>
                  </RadioCards.Root>
                )}
              />
            )}
          </FormField>

          <FormField
            label="On a scale of 1 to 10, how would you rate the overall difficulty of the challenges in this event?"
            error={errors.difficulty_rating}
          >
            {(injected) => (
              <Controller
                name="difficulty_rating"
                control={control}
                render={({ field }) => (
                  <SegmentedControl.Root
                    value={String(field.value)}
                    onValueChange={(v) => { field.onChange(Number(v)); }}
                    onBlur={field.onBlur}
                    ref={field.ref}
                    {...injected}
                  >
                    {scale}
                  </SegmentedControl.Root>
                )}
              />
            )}
          </FormField>

          <FormField
            label="On a scale of 1 to 10, how relevant were the challenges to CISA's intended NICE Work Roles?"
            error={errors.relevancy_rating}
          >
            {(injected) => (
              <Controller
                name="relevancy_rating"
                control={control}
                render={({ field }) => (
                  <SegmentedControl.Root
                    value={String(field.value)}
                    onValueChange={(v) => { field.onChange(Number(v)); }}
                    onBlur={field.onBlur}
                    ref={field.ref}
                    {...injected}
                  >
                    {scale}
                  </SegmentedControl.Root>
                )}
              />
            )}
          </FormField>

          <FormField
            label="On a scale of 1 to 10, how engaging did you find the challenges throughout the event?"
            error={errors.engagement_rating}
          >
            {(injected) => (
              <Controller
                name="engagement_rating"
                control={control}
                render={({ field }) => (
                  <SegmentedControl.Root
                    value={String(field.value)}
                    onValueChange={(v) => { field.onChange(Number(v)); }}
                    onBlur={field.onBlur}
                    ref={field.ref}
                    {...injected}
                  >
                    {scale}
                  </SegmentedControl.Root>
                )}
              />
            )}
          </FormField>

          <FormField
            label={`Please share your thoughts on the challenges in this event. What aspects did you find most difficult, 
              most relevant to your role, or most engaging? Feel free to mention specific challenges or areas that stood out to you.`}
            rightComponent={(
              <Text size="2" color="gray" className="[label[data-invalid=true]+&]:!text-(--red-11)">
                {CHAR_LIMIT - (watch('thoughts') || '').length}
              </Text>
            )}
            error={errors.thoughts}
          >
            {(injected) => (
              <TextArea
                rows={3}
                {...register('thoughts', { maxLength : { value : CHAR_LIMIT, message : `Feedback cannot exceed ${CHAR_LIMIT} characters.` } })}
                placeholder="Please specify..."
                {...injected}
              />
            )}
          </FormField>

          <FormField
            label={`How can we improve the next President's Cup? Please provide any feedback on event structure, challenge difficulty, 
              communication, or other aspects.`}
            rightComponent={(
              <Text size="2" color="gray" className="[label[data-invalid=true]+&]:!text-(--red-11)">
                {CHAR_LIMIT - (watch('additional_feedback') || '').length}
              </Text>
            )}
            error={errors.additional_feedback}
          >
            {(injected) => (
              <TextArea
                rows={3}
                {...register('additional_feedback', { maxLength : { value : CHAR_LIMIT, message : `Feedback cannot exceed ${CHAR_LIMIT} characters.` } })}
                placeholder="Please specify..."
                {...injected}
              />
            )}
          </FormField>

          <FormField
            label={`What additional cybersecurity topics or skills would you like to see covered in future President's Cup challenges?`}
            rightComponent={(
              <Text size="2" color="gray" className="[label[data-invalid=true]+&]:!text-(--red-11)">
                {CHAR_LIMIT - (watch('additional_topics') || '').length}
              </Text>
            )}
            error={errors.additional_topics}
          >
            {(injected) => (
              <TextArea
                rows={3}
                {...register('additional_topics', { maxLength : { value : CHAR_LIMIT, message : `Feedback cannot exceed ${CHAR_LIMIT} characters.` } })}
                placeholder="Please specify..."
                {...injected}
              />
            )}
          </FormField>

          <InfoCallout>
            You may also provide feedback for specific challenges by navigating to a challenge and selecting the &quot;Feedback&quot; option in its sidebar.
            <br />
            Be sure to submit this form first to avoid losing your responses!
          </InfoCallout>

          <Flex direction="row-reverse">
            <Button
              type="submit"
              color={COLOR_POSITIVE}
              loading={buttonState === 'loading'}
              disabled={buttonState !== null}
              className="!w-48"
            >
              {buttonState === 'success' ? (
                <>
                  <TbCheck />
                  Saved
                </>
              ) : (
                <>
                  <TbSend />
                  Submit Feedback
                </>
              )}
            </Button>
          </Flex>

        </Flex>
      </form>
    </Container>
  );
}
