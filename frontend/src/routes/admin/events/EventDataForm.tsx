import type { Event } from '@/types';
import {
  Box,
  Flex,
  Switch,
  TextArea,
  TextField,
} from '@radix-ui/themes';
import FormField from 'components/FormField';
import { Controller, type UseFormReturn } from 'react-hook-form';

export default function EventDataForm({
  rhf,
}: {
  rhf: UseFormReturn<Omit<Event, 'id'>>,
}) {
  const { register, formState : { errors } } = rhf;

  return (
    <>
      <FormField label="Name" error={errors.name}>
        {(injected) => (
          <TextField.Root
            placeholder="Event Name"
            {...register('name', {
              required : 'Event name is required',
            })}
            {...injected}
          />
        )}
      </FormField>

      <FormField label="Description" error={errors.description}>
        {(injected) => (
          <TextArea
            placeholder="Event Description"
            rows={4}
            resize="vertical"
            {...register('description')}
            {...injected}
          />
        )}
      </FormField>

      <Flex direction="row" gap="2" className="*:grow *:basis-0">

        <FormField label="Public" error={errors.public}>
          {(injected) => (
            <Controller
              control={rhf.control}
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

        <FormField label="Hints Enabled" error={errors.hints_enabled}>
          {(injected) => (
            <Controller
              control={rhf.control}
              name="hints_enabled"
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

        <FormField label="Teams Locked" error={errors.locked}>
          {(injected) => (
            <Controller
              control={rhf.control}
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

      </Flex>

      <Flex direction="row" gap="2" className="*:grow *:basis-0">
        <FormField label="Max Team Size" error={errors.max_team_size}>
          {(injected) => (
            <TextField.Root
              type="number"
              {...register('max_team_size', {
                required : 'Max team size is required',
                valueAsNumber : true,
                min : {
                  value : 1,
                  message : 'Max team size must be at least 1',
                },
                max : {
                  value : 8,
                  message : 'Max team size cannot exceed 8',
                },
              })}
              {...injected}
            />
          )}
        </FormField>

        <FormField label="Time Limit (minutes)" error={errors.time_limit_minutes}>
          {(injected) => (
            <TextField.Root
              type="number"
              placeholder="No time limit"
              step={1}
              {...register('time_limit_minutes', {
                valueAsNumber : true,
                min : {
                  value : 1,
                  message : 'Time limit must be at least 1 minute',
                },
              })}
              {...injected}
            />
          )}
        </FormField>
      </Flex>

      <Flex direction="row" gap="2" className="*:grow *:basis-0">
        <FormField label="Registration Opens" error={errors.registration_start_date}>
          {(injected) => (
            <TextField.Root
              type="datetime-local"
              {...register('registration_start_date', {
                valueAsDate : true,
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
                valueAsDate : true,
              })}
              {...injected}
            />
          )}
        </FormField>
      </Flex>

      <Flex direction="row" gap="2" className="*:grow *:basis-0">
        <FormField label="Event Starts" error={errors.start_time}>
          {(injected) => (
            <TextField.Root
              type="datetime-local"
              {...register('start_time', {
                valueAsDate : true,
              })}
              {...injected}
            />
          )}
        </FormField>
        <FormField label="Event Ends" error={errors.end_time}>
          {(injected) => (
            <TextField.Root
              type="datetime-local"
              {...register('end_time', {
                valueAsDate : true,
              })}
              {...injected}
            />
          )}
        </FormField>
      </Flex>
    </>
  );
}
