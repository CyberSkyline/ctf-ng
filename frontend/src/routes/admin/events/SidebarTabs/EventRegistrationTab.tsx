import type { Event } from '@/types';
import { adjustDateForInput } from '@/util';
import { omit } from 'lodash'
import { Box, Flex, TextField, Switch } from '@radix-ui/themes';
import Statistic from 'components/Statistic';
import ActionButtonsGroup from './ActionButtonsGroup';
import { useState } from 'react'
import { Controller, useForm } from 'react-hook-form'
import FormField from 'components/FormField';

export default function EventRegistrationTab({ event }: { event: Event }) {
  const [isEditing, setIsEditing] = useState<boolean>(false)

  const {
    control,
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<Event>({
    defaultValues: {
      ...omit(event, 'id'),
      registration_start_date: adjustDateForInput(event?.registration_start_date || null) as unknown as Date,
      registration_end_date: adjustDateForInput(event?.registration_end_date || null) as unknown as Date,
      start_time: adjustDateForInput(event?.start_time || null) as unknown as Date,
      end_time: adjustDateForInput(event?.end_time || null) as unknown as Date,
      image: event?.image || 'None',
    }
  })

  const update = async (data: Event) => {
    // This is going to end up being a PUT
    console.log('update', data)
  }

  return (
    <Flex direction="column" gap="3" className='mb-4'>
      <ActionButtonsGroup
        isEditing={isEditing}
        setIsEditing={setIsEditing}
        reset={reset}
        cancelOnly={true}
      />
      {isEditing ? (
        <form
          onSubmit={handleSubmit(update)}
          className='space-y-4'
        >
          <FormField label="Public" error={errors.public}>
            {(injected) => (
              <Controller
                control={control}
                name="public"
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

          <FormField label="Teams Locked" error={errors.locked}>
            {(injected) => (
              <Controller
                control={control}
                name="locked"
                defaultValue={false}
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

          <FormField label="Registration Open" error={errors.registration_open}>
            {(injected) => (
              <Controller
                control={control}
                name="registration_open"
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

          <FormField label="Registration Starts" error={errors.registration_start_date}>
            {(injected) => (
              <TextField.Root
                type="datetime-local"
                {...register('registration_start_date', {
                  valueAsDate: true,
                })}
                {...injected}
              />

            )}
          </FormField>

          <FormField label="Registration Closes" error={errors.registration_end_date}>
            {(injected) => (
              <TextField.Root
                type="datetime-local"
                {...register('registration_end_date', {
                  valueAsDate: true,
                })}
                {...injected}
              />
            )}
          </FormField>

          <ActionButtonsGroup
            isEditing={isEditing}
            setIsEditing={setIsEditing}
            reset={reset}
          />
        </form>
      ) : (
        <>
          <Statistic label="Visibility" value={event.public ? 'Public' : 'Private'} />
          <Statistic label="Teams Locked" value={event.locked ? 'Yes' : 'No'} />
          <Statistic label="Registration Open" value={event.registration_open ? 'Yes' : 'No'} />
          <Statistic label="Registration Starts" value={event.registration_start_date?.toLocaleString() || 'N/A'} />
          <Statistic label="Registration Ends" value={event.registration_end_date?.toLocaleString() || 'N/A'} />
        </>
      )}
    </Flex>
  );
}
