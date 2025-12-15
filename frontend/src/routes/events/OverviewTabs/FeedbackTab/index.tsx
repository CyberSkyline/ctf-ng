import { COLOR_POSITIVE } from '@/constants';
import { submitEventFeedback, useMyEventFeedback } from '@/hooks/feedback';
import {
  Button,
  Container,
  Flex,
  RadioCards,
  Strong,
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
  cyberExperience: string,
  participationReason: string,
  participationAgain: string,
  additionalFeedback: string,
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

const PARTICIPATION_REASONS: Record<string, string> = {
  'Promotional messages about the President\'s Cup' : 'Emails, social media, presentation, etc.',
  'Word-of-Mouth' : 'A supervisor, colleague or friend encouraged me to register.',
  'Returning Participant' : 'Enjoyed the event and wanted to participate in it again.',
  'Professional Development' : 'A chance to grow my cybersecurity skills.',
};

export default function FeedbackTab() {
  const { idEvent } = useParams<{idEvent: string}>();
  const eventId = Number(idEvent);
  const { data : currentFeedback, error : currentFeedbackError } = useMyEventFeedback(eventId);

  const {
    register, reset, control, handleSubmit, formState : { errors },
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
                render={({ field }) => (
                  <RadioCards.Root
                    value={field.value || null}
                    onValueChange={(e) => {
                      field.onChange(e);
                    }}
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
                    <RadioCards.Item value="High School Diploma/GED">
                      High School Diploma/GED
                    </RadioCards.Item>

                    <RadioCards.Item value="Associate Degree">
                      Associate Degree
                    </RadioCards.Item>

                    <RadioCards.Item value="Other (Some College)">
                      Other (Some College)
                    </RadioCards.Item>

                    <RadioCards.Item value="Bachelor's Degree">
                      Bachelor&apos;s Degree
                    </RadioCards.Item>

                    <RadioCards.Item value="Master's Degree">
                      Master&apos;s Degree
                    </RadioCards.Item>

                    <RadioCards.Item value="PhD">
                      PhD
                    </RadioCards.Item>
                  </RadioCards.Root>
                )}
              />
            )}
          </FormField>

          <FormField
            label="How many years of cybersecurity experience do you have?"
            error={errors.cyberExperience}
          >
            {(injected) => (
              <Controller
                name="cyberExperience"
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
            error={errors.participationReason}
          >
            {(injected) => (
              <Controller
                name="participationReason"
                control={control}
                render={({ field }) => (
                  <RadioCards.Root
                    value={field.value || null}
                    onValueChange={field.onChange}
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
            error={errors.participationAgain}
          >
            {(injected) => (
              <Controller
                name="participationAgain"
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
            error={errors.additionalFeedback}
          >
            {(injected) => (
              <TextArea
                rows={3}
                {...register('additionalFeedback')}
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
