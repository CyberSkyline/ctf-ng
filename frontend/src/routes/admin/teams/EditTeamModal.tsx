import { COLOR_WARNING } from '@/constants';
import { adminUpdateTeam } from '@/hooks/team';
import type { Team } from '@/types';
import {
  Button,
  TextField,
  Flex,
  SegmentedControl,
} from '@radix-ui/themes';
import FormField from 'components/FormField';
import Modal from 'components/Modal';
import { pick } from 'lodash';
import { Controller, type DefaultValues } from 'react-hook-form';
import { TbPencil } from 'react-icons/tb';

function adjustDateForInput(date: Date | null): string | null {
  // Adjust the date to be in the format required by datetime-local input
  if (date === null) return null;
  const dateObj = new Date(date);
  const offset = dateObj.getTimezoneOffset();
  const localDate = new Date(dateObj.getTime() - (offset * 60 * 1000));
  return localDate.toISOString().slice(0, 16);
}

export default function EditTeamModal({
  teamToUpdate,
}: {
  teamToUpdate: Team;
}) {
  const handleSubmit = async (data: Pick<Team, 'name' | 'ranked' | 'start_timestamp' | 'end_time'>) => adminUpdateTeam(teamToUpdate.id, data);

  // Default value Dates must be converted to datetime-local string format, even though the value is typed as Date.
  // This is because valueAsDate only applies to entered values, not default values.
  const defaultValues: DefaultValues<Pick<Team, 'name' | 'ranked' | 'start_timestamp' | 'end_time'>> = {
    ...pick(teamToUpdate, [ 'name', 'ranked' ]),
    start_timestamp : adjustDateForInput(teamToUpdate.start_timestamp || null) as unknown as Date,
    end_time : adjustDateForInput(teamToUpdate.end_time || null) as unknown as Date,
  };

  return (
    <Modal
      title="Edit Team"
      trigger={(
        <Button variant="soft" color={COLOR_WARNING}>
          <TbPencil />
          Edit
        </Button>
      )}
      onSubmit={handleSubmit}
      submitVerb="Update"
      submitColor={COLOR_WARNING}
      defaultValues={defaultValues}
    >
      {({ register, control, formState : { errors } }) => (
        <>
          <FormField label="Name" error={errors.name}>
            {(injected) => (
              <TextField.Root
                {...register('name', { required : 'Name is required' })}
                {...injected}
              />
            )}
          </FormField>
          <Controller
            name="ranked"
            control={control}
            render={({ field }) => (
              <FormField label="Leaderboard Status" error={errors.ranked}>
                {(injected) => (
                  <SegmentedControl.Root
                    {...field}
                    {...injected}
                    value={field.value ? 'ranked' : 'unranked'}
                    onValueChange={(value) => field.onChange(value === 'ranked')}
                  >
                    <SegmentedControl.Item value="ranked">Ranked</SegmentedControl.Item>
                    <SegmentedControl.Item value="unranked">Unranked</SegmentedControl.Item>
                  </SegmentedControl.Root>
                )}
              </FormField>
            )}
          />
          <Flex direction="row" gap="2" className="*:grow *:basis-0">
            <FormField label="Start Timestamp" error={errors.start_timestamp}>
              {(injected) => (
                <TextField.Root
                  type="datetime-local"
                  {...register('start_timestamp', {
                    valueAsDate : true,
                  })}
                  {...injected}
                />
              )}
            </FormField>
            <FormField label="End Timestamp" error={errors.end_time}>
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
      )}
    </Modal>
  );
}
