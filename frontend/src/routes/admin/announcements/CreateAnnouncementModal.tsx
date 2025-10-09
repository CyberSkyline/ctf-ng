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
import { addNewAnnouncement } from '@/hooks/notifications';
import { TbPlus } from 'react-icons/tb';
import { Controller } from 'react-hook-form';
import { useState } from 'react';

export default function CreateAnnoucementModal() {
  const [ selectedOption, setSelectedOption ] = useState<'general' | 'event'>('general');
  
  const handleSubmit = async (data: {event: string, title: string, message: string, send_notification: boolean, expires_at: Date, type: string}) => {
    if(selectedOption === 'general'){
      console.log('ann', data)
      //addNewAnnouncement(data);
    } else {
      console.log('event ann', data)
    }
  }

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
        event: 'None',
        send_notification : false,
        expires_at : null as unknown as Date,
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
            <SegmentedControl.Item value="event">
              Event
            </SegmentedControl.Item>
          </SegmentedControl.Root>

          {selectedOption === 'event' && (
            <div>dropdown here</div>
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
