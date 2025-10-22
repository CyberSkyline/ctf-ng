import {
  Box,
  Button,
  Container,
  Flex,
  Heading,
  TextField,
} from '@radix-ui/themes';
import { TbArrowLeft } from 'react-icons/tb';
import { useNavigate } from 'react-router';
import { useState } from 'react';
import { isUndefined, map } from 'lodash';
import {
  Controller,
  useForm,
  type FieldError,
  type Control,
} from 'react-hook-form';
import RichTextEditor from 'components/RichTextEditor';
import FormField from 'components/FormField';
import SelectDropdown from 'components/SelectDropdown';
import RequireEventPermission from 'components/RequireEventPermission';
import { ErrorCallout } from 'components/Callouts';
import { createTicket } from '@/hooks/support';
import { useMyEvents } from '@/hooks/events';
import { useMyChallenges } from '@/hooks/challenge';

type CreateInputs = {
  subject: string,
  text: string,
  event_id?: string,
  challenge_id?: string,
}

function ChallengesDropdown({ control, error, eventId }: {control: Control<CreateInputs>, error?: FieldError, eventId: number}) {
  const { data : challenges, error : challengeError } = useMyChallenges(eventId);
  const challengeOptions: {value: string, name: string}[] = map(
    challenges,
    (chall) => ({ value : chall.challenge_id.toString(), name : chall.challenge_name }),
  );

  if (!isUndefined(challengeError)) {
    return <ErrorCallout>{challengeError?.message}</ErrorCallout>;
  }
  return (
    <SelectDropdown
      control={control}
      rules={{
        validate : (value) => value !== '' || 'Please select a challenge or None',
      }}
      error={error}
      name="challenge_id"
      label="Challenge"
      options={challengeOptions}
      noneOption
    />
  );
}

export default function CreateTicket() {
  const navigate = useNavigate();

  const {
    control,
    register,
    handleSubmit,
    formState : { errors },
    watch,
  } = useForm<CreateInputs>({
    defaultValues : {
      subject : undefined,
      text : undefined,
      event_id : '',
      challenge_id : '',
    },
  });

  const watchedEvent: string | undefined = watch('event_id');

  const [ error, setError ] = useState<string | null>(null);
  const [ loading, setLoading ] = useState<boolean>(false);

  const { data : events, error : eventsError } = useMyEvents();
  const eventOptions: {value: string, name: string}[] = map(events, ({ id, name }) => ({ value : id.toString(), name }));

  if (!isUndefined(eventsError)) {
    return <ErrorCallout>{eventsError?.message}</ErrorCallout>;
  }

  const create = async (data: CreateInputs) => {
    setLoading(true);

    createTicket({
      subject : data.subject,
      text : data.text,
      event_id : Number(data.event_id) || undefined,
      challenge_id : Number(data.challenge_id) || undefined,
    }).then((ticketId) => {
      navigate(`/support/${ticketId}`);
    }).catch((err) => {
      setError(err.message);
    }).finally(() => {
      setLoading(false);
    });
  };

  return (
    <Container size="4">
      <title>Create Support Ticket</title>
      <Flex gap="3" direction="column">
        <Box maxWidth="200px">
          <Button
            variant="ghost"
            onClick={() => { navigate('/support'); }}
          >
            <TbArrowLeft />
            Support
          </Button>
        </Box>
        <Heading size="7">Create a New Support Ticket</Heading>

        <form
          onSubmit={handleSubmit(create)}
        >
          <FormField label="Subject" error={errors?.subject}>
            {(injected) => (
              <TextField.Root
                placeholder="Subject"
                {...register('subject', { required : 'Subject is required' })}
                {...injected}
              />
            )}
          </FormField>
          <FormField label="Message" error={errors?.text}>
            {() => (
              <Controller
                name="text"
                control={control}
                rules={{ required : 'Message is required' }}
                render={({ field }) => (
                  <RichTextEditor
                    initialValue={field.value}
                    onChange={field.onChange}
                  />
                )}
              />
            )}
          </FormField>

          <SelectDropdown
            control={control}
            rules={{
              validate : (value) => value !== '' || 'Please select an event or None',
            }}
            error={errors?.event_id}
            name="event_id"
            label="Event"
            options={eventOptions}
            noneOption
          />

          {watchedEvent !== 'None'
            && (
              <RequireEventPermission
                eventId={Number(watchedEvent)}
                permission="CAN_VIEW_CHALLENGES"
                permissionDeniedPlaceholder={null}
              >
                <ChallengesDropdown
                  control={control}
                  error={errors?.challenge_id}
                  eventId={Number(watchedEvent)}
                />
              </RequireEventPermission>
            )}

          {error && <ErrorCallout className="mt-2">{error}</ErrorCallout>}
          <Button
            type="submit"
            className="!mt-2"
            loading={loading}
            disabled={loading}
          >
            Submit Ticket
          </Button>
        </form>

      </Flex>
    </Container>
  );
}
