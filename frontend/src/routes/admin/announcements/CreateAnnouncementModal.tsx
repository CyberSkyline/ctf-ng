import { COLOR_POSITIVE } from '@/constants';
import FormField from 'components/FormField';
import Modal from 'components/Modal';
import {
  Button,
  Box,
  Switch,
  TextArea,
  TextField,
  SegmentedControl,
} from '@radix-ui/themes';
import { addNewAnnouncement, addNewEventAnnouncement } from '@/hooks/notifications';
import { useAllEvents } from '@/hooks/events';
import { TbPlus } from 'react-icons/tb';
import { Controller } from 'react-hook-form';
import { useState } from 'react';
import SelectDropdown from 'components/SelectDropdown';
import { isNull, map } from 'lodash';
import { ErrorCallout } from 'components/Callouts';

export default function CreateAnnoucementModal() {
  const { data : allEvents, error : allEventsError, isLoading } = useAllEvents();
  const eventOptions: {value: string, name: string}[] = map(allEvents, ({ id, name }) => ({ value : id.toString(), name }));

  const [ selectedOption, setSelectedOption ] = useState<'general' | 'event'>('general');

  const handleSubmit = async (data: {event_id: string, title: string, message: string, send_notification: boolean, expires_at: Date, type: string}) => {
    if (selectedOption === 'general') {
      addNewAnnouncement(data);
    } else {
      addNewEventAnnouncement(data);
    }
  };

  return (
    <Modal
      title="Create Announcement"
      trigger={(
        <Button variant="solid" color={COLOR_POSITIVE}>
          <TbPlus />
          Create Announcement
        </Button>
      )}
      onSubmit={handleSubmit}
      submitVerb="Send"
      submitColor={COLOR_POSITIVE}
      defaultValues={{
        event_id : '',
        send_notification : false,
        expires_at : null as unknown as Date,
        type : 'event_update',
      }}
    >
      {({ register, control, formState : { errors } }) => (
        <>
          <SegmentedControl.Root
            value={selectedOption}
            onValueChange={(val) => setSelectedOption(val as 'general' | 'event')}
            className="!h-16"
          >
            <SegmentedControl.Item value="general">
              General
            </SegmentedControl.Item>
            {!isLoading && !isNull(allEvents) && (
              <SegmentedControl.Item value="event">
                Event
              </SegmentedControl.Item>
            )}
          </SegmentedControl.Root>
          {allEventsError && <ErrorCallout>{allEventsError.message}</ErrorCallout>}

          {selectedOption === 'event' && (
            <>
              <SelectDropdown
                control={control}
                rules={{
                  validate : (value) => value !== '' || 'Please select an event',
                }}
                error={errors?.event_id}
                name="event_id"
                label="Event"
                options={eventOptions}
                noneOption={false}
              />
              <SelectDropdown
                control={control}
                error={errors?.type}
                name="type"
                label="Type"
                noneOption={false}
                options={[
                  { value : 'event_update', name : 'Event Update' },
                  { value : 'general', name : 'General' },
                  { value : 'event_start', name : 'Event Start' },
                  { value : 'event_end', name : 'Event End' },
                  { value : 'leaderboard_update', name : 'Leaderboard Update', icon : <TbPlus /> },
                ]}
              />
            </>
          )}

          <FormField label="Title" error={errors?.title}>
            {(injected) => (
              <TextField.Root
                placeholder="Announcement Title"
                {...register('title', {
                  required : 'Title is required',
                })}
                {...injected}
              />
            )}
          </FormField>
          <FormField label="Message" error={errors?.message}>
            {(injected) => (
              <TextArea
                placeholder="Messsage"
                rows={4}
                resize="vertical"
                {...register('message', {
                  required : 'Message is required',
                })}
                {...injected}
              />
            )}
          </FormField>
          <FormField label="Expiration Date" error={errors.expires_at}>
            {(injected) => (
              <TextField.Root
                type="datetime-local"
                {...register('expires_at', {
                  valueAsDate : true,
                })}
                {...injected}
              />

            )}
          </FormField>
          <FormField label="Send Notification" error={errors.send_notification}>
            {(injected) => (
              <Controller
                control={control}
                name="send_notification"
                defaultValue
                rules={{}}
                render={({ field }) => (
                  <Box>
                    <Switch
                      checked={field.value}
                      onCheckedChange={(checked) => {
                        field.onChange(checked);
                      }}
                      name={field.name}
                      ref={field.ref}
                      size="3"
                      {...injected}
                    />
                  </Box>
                )}
              />
            )}
          </FormField>

        </>
      )}
    </Modal>
  );
}
