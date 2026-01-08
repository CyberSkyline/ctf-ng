import type { Event } from '@/types';
import { adjustDateForInput } from '@/util';
import { omit } from 'lodash';
import {
  Box,
  Flex,
  TextField,
  Switch,
} from '@radix-ui/themes';
import Statistic from 'components/Statistic';
import { useState } from 'react';
import { Controller, useForm } from 'react-hook-form';
import FormField from 'components/FormField';
import { ErrorCallout } from 'components/Callouts';
import { updateEvent } from '@/hooks/events';
import ActionButtonsGroup from './ActionButtonsGroup';

export default function EventGameplayTab({ event }: { event: Event }) {
  const [ isEditing, setIsEditing ] = useState<boolean>(false);
  const [ loading, setLoading ] = useState<boolean>(false);
  const [ error, setError ] = useState<string| null>(null);

  const {
    control,
    register,
    handleSubmit,
    formState : { errors },
    reset,
  } = useForm<Event>({
    defaultValues : {
      ...omit(event, 'id'),
      start_time : adjustDateForInput(event?.start_time || null) as unknown as Date,
      end_time : adjustDateForInput(event?.end_time || null) as unknown as Date,
    },
  });

  const update = async (data: Event) => {
    setLoading(true);
    setError(null);

    updateEvent(event.id, data).then(() => {
      setIsEditing(false);
      reset(data);
    }).catch((err) => {
      setError(err.message);
    }).finally(() => {
      setLoading(false);
    });
  };

  return (
    <Flex direction="column" gap="3" className="mb-4">
      <ActionButtonsGroup
        isEditing={isEditing}
        setIsEditing={setIsEditing}
        reset={() => {
          reset();
          setError(null);
        }}
        cancelOnly
      />
      {isEditing ? (
        <form
          onSubmit={handleSubmit(update)}
          className="space-y-4"
        >
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
          <FormField label="Hints Enabled" error={errors.hints_enabled}>
            {(injected) => (
              <Controller
                control={control}
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
          <FormField label="Show Leaderboard" error={errors.show_leaderboard}>
            {(injected) => (
              <Controller
                control={control}
                name="show_leaderboard"
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

          {error && <ErrorCallout>{error}</ErrorCallout>}

          <ActionButtonsGroup
            isEditing={isEditing}
            setIsEditing={setIsEditing}
            reset={() => {
              reset();
              setError(null);
            }}
            loading={loading}
          />
        </form>
      ) : (
        <>
          <Statistic label="Max Team Size" value={event.max_team_size} />
          <Statistic label="Event Starts" value={event.start_time?.toLocaleString() || 'N/A'} />
          <Statistic label="Event Ends" value={event.end_time?.toLocaleString() || 'N/A'} />
          <Statistic label="Time Limit" value={event.time_limit_minutes ? `${event.time_limit_minutes} minutes` : 'N/A'} />
          <Statistic label="Hints Enabled" value={event.hints_enabled ? 'Yes' : 'No'} />
          <Statistic label="Leaderboard Visible" value={event.show_leaderboard ? 'Yes' : 'No'} />
        </>
      )}
    </Flex>
  );
}
