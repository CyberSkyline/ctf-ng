import { COLOR_POSITIVE } from '@/constants';
import { submitEventFeedback, useMyEventFeedback } from '@/hooks/feedback';
import {
  Button,
  Container,
  Flex,
  RadioCards,
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
  education: string,
  cyber_experience: string,
  participation_reason: string,
  participation_again: string,
  additional_feedback: string,
}>

const ROLES = [
  'Cyber Defense Incident Responder',
  'Cyber Defense Forensics Analyst',
  'Network Operations Specialist',
  'Cyber Defense Analyst',
  'Exploitation Analyst',
  'Cyber Operator',
  'Research and Development Specialist',
  'Vulnerability Assessment Analyst',
  'Data Analyst',
  'Threat/Warning Analyst',
];

const EDUCATION_LEVELS = [
  'High School Diploma/GED',
  'Associate Degree',
  'Other (Some College)',
  'Bachelor\'s Degree',
  'Master\'s Degree',
  'PhD',
];

const PARTICIPATION_REASONS: Record<string, string> = {
  'Promotional messages about the President\'s Cup' : 'Emails, social media, presentation, etc.',
  'Word-of-Mouth' : 'A supervisor, colleague or friend encouraged me to register.',
  'Returning Participant' : 'Enjoyed the event and wanted to participate in it again.',
  'Professional Development' : 'A chance to grow my cybersecurity skills.',
};

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
            label="What NICE work role best aligns with your position?"
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
            label="Please indicate your highest level of education."
            error={errors.education}
          >
            {(injected) => (
              <Controller
                name="education"
                control={control}
                render={({ field }) => (
                  <RadioCards.Root
                    value={field.value || null}
                    onValueChange={field.onChange}
                    columns="3"
                    gap="1"
                    {...injected}
                  >
                    {EDUCATION_LEVELS.map((level) => (
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
            label="How many years of cybersecurity experience do you have?"
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
                    columns="5"
                    gap="1"
                    {...injected}
                  >
                    <RadioCards.Item value="1-5">
                      1-5
                    </RadioCards.Item>

                    <RadioCards.Item value="5-10">
                      5-10
                    </RadioCards.Item>

                    <RadioCards.Item value="10-15">
                      10-15
                    </RadioCards.Item>

                    <RadioCards.Item value="15+">
                      15+
                    </RadioCards.Item>

                    <RadioCards.Item value="N/A">
                      N/A
                    </RadioCards.Item>
                  </RadioCards.Root>
                )}
              />
            )}
          </FormField>

          <FormField
            label="What made you decide to participate?"
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
                      Unsure
                    </RadioCards.Item>
                  </RadioCards.Root>
                )}
              />
            )}
          </FormField>

          <FormField
            label="How can we improve the next President’s Cup? Please provide any other feedback you would like to share."
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
