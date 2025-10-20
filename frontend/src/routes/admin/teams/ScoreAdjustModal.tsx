import { COLOR_WARNING } from '@/constants';
import { adjustPoints } from '@/hooks/scoring';
import type { Team } from '@/types';
import { Button, TextField } from '@radix-ui/themes';
import FormField from 'components/FormField';
import Modal from 'components/Modal';
import { TbPlusMinus } from 'react-icons/tb';

export default function ScoreAdjustModal({ team }: { team: Team }) {
  const handleSubmit = async ({
    adjustment,
    reason,
  }: {
    adjustment: number;
    reason: string;
  }) => adjustPoints(team.event_id, team.id, adjustment, reason);

  return (
    <Modal
      title="Point Adjust"
      description={`Apply a manual score adjustment to ${team.name}.`}
      trigger={(
        <Button variant="soft" color={COLOR_WARNING}>
          <TbPlusMinus />
          Adjust Score
        </Button>
      )}
      onSubmit={handleSubmit}
      submitVerb="Adjust"
      submitColor={COLOR_WARNING}
    >
      {({ register, formState : { errors } }) => (

        <>
          <FormField label="Adjustment" error={errors?.adjustment}>
            {(injected) => (
              <TextField.Root
                placeholder="Number of points"
                type="number"
                {...register('adjustment', {
                  required : 'Point value is required',
                  valueAsNumber : true,
                })}
                {...injected}
              />
            )}
          </FormField>
          <FormField label="Reason" error={errors?.reason}>
            {(injected) => (
              <TextField.Root
                placeholder="Reason for adjustment"
                {...register('reason', { required : 'Reason is required' })}
                {...injected}
              />
            )}
          </FormField>
        </>

      )}

    </Modal>
  );
}
