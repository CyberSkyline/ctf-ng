import { COLOR_POSITIVE, COLOR_WARNING } from '@/constants';
import FormField from 'components/FormField';
import Modal from 'components/Modal';
import {
  Button,
  Box,
  Switch,
  TextField,
  SegmentedControl,
} from '@radix-ui/themes';
import { addNewAnnouncement, addNewEventAnnouncement, updateAnnouncement } from '@/hooks/announcements';
import { useAllEvents } from '@/hooks/events';
import type { Announcement } from '@/types';
import { adjustDateForInput } from '@/util';
import { TbPencil, TbPlus } from 'react-icons/tb';
import { Controller, type DefaultValues } from 'react-hook-form';
import { useState } from 'react';
import RichTextEditor from 'components/RichTextEditor';
import SelectDropdown from 'components/SelectDropdown';
import {
  isNull,
  isUndefined,
  map,
  pick,
} from 'lodash';
import { ErrorCallout } from 'components/Callouts';

interface AnnouncementForm {
  event_id: string,
  title: string,
  message: string,
  send_notification: boolean,
  expires_at: Date,
  type: string,
}

export default function AnnouncementModal({ announcement }: {announcement?: Announcement}) {
  const { data : allEvents, error : allEventsError, isLoading } = useAllEvents();
  const eventOptions: {value: string, name: string}[] = map(allEvents, ({ id, name }) => ({ value : id.toString(), name }));

  const isEditing = !isUndefined(announcement);
  const isEventAnnouncement = !isUndefined(announcement?.event_id);
  const [ selectedOption, setSelectedOption ] = useState<'general' | 'event'>('general');

  const handleSubmit = async (data: AnnouncementForm) => {
    if (!isUndefined(announcement)) {
      return updateAnnouncement(announcement.id, pick(data, [ 'title', 'message', 'type', 'expires_at' ]));
    }
    if (selectedOption === 'general') {
      return addNewAnnouncement(data);
    }
    return addNewEventAnnouncement(data);
  };

  // Default values must be converted to datetime-local string format.
  const defaultValues: DefaultValues<AnnouncementForm> = announcement
    ? {
      ...pick(announcement, [ 'title', 'message', 'type' ]),
      expires_at : adjustDateForInput(announcement.expires_at) as unknown as Date,
    }
    : {
      event_id : '',
      send_notification : false,
      expires_at : null as unknown as Date,
      type : 'event_update',
    };

  return (
    <Modal
      title={isEditing ? 'Edit Announcement' : 'Create Announcement'}
      trigger={(
        <Button
          variant={isEditing ? 'soft' : 'solid'}
          color={isEditing ? COLOR_WARNING : COLOR_POSITIVE}
        >
          {isEditing ? <TbPencil /> : <TbPlus />}
          {isEditing ? 'Edit' : 'Create Announcement'}
        </Button>
      )}
      onSubmit={handleSubmit}
      submitVerb={isEditing ? 'Update' : 'Send'}
      submitColor={isEditing ? COLOR_WARNING : COLOR_POSITIVE}
      defaultValues={defaultValues}
    >
      {({ register, control, formState : { errors } }) => (
        <>
          {!isEditing && (
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
              )}
            </>
          )}

          {(isEventAnnouncement || selectedOption === 'event') && (
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
            {() => (
              <Controller
                control={control}
                name="message"
                rules={{ required : 'Message is required' }}
                render={({ field }) => (
                  <RichTextEditor initialValue={field.value} onChange={field.onChange} />
                )}
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
          {!isEditing && (
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
          )}
        </>
      )}
    </Modal>
  );
}
