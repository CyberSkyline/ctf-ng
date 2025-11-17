import { COLOR_WARNING } from '@/constants';
import { updateTeamName, useMyTeam } from '@/hooks/events';
import type { Event } from '@/types';
import { Button, TextField } from '@radix-ui/themes';
import FormField from 'components/FormField';
import Modal from 'components/Modal';
import { TbPencil } from 'react-icons/tb';

export default function RenameTeamModal({ event }: {event: Event}) {
  const isIndividual = event?.max_team_size === 1;
  const { data : myTeam } = useMyTeam(event.id);

  const handleRename = async (data: { name: string }) => updateTeamName(event.id, data.name);

  return (
    <Modal
      title={isIndividual ? 'Change Name' : 'Rename Team'}
      description={`Change your${isIndividual ? '' : ' team\'s'} name as it appears on the leaderboard.`}
      trigger={(
        <Button variant="ghost" color={COLOR_WARNING} disabled={!myTeam}>
          <TbPencil />
          {isIndividual ? 'Change Name' : 'Rename Team'}
        </Button>
      )}
      onSubmit={handleRename}
      submitVerb="Rename"
      defaultValues={{ name : myTeam?.name || '' }}
    >
      {({ register, formState : { errors } }) => (
        <FormField label={isIndividual ? 'New Name' : 'New Team Name'} error={errors?.name}>
          {(injected) => <TextField.Root {...register('name', { required : true, maxLength : 100 })} {...injected} />}
        </FormField>
      )}
    </Modal>
  );
}
