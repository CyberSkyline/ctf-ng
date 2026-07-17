import Modal from '@/components/Modal';
import { COLOR_POSITIVE, COLOR_WARNING } from '@/constants';
import { Button } from '@radix-ui/themes';
import { createSponsor, editSponsor } from '@/hooks/sponsors';
import type { Sponsor } from '@/types';
import { isUndefined, omit } from 'lodash';
import SponsorDataForm from './SponsorDataForm';

export default function SponsorModal({ sponsor }: {sponsor?: Sponsor}) {
  const isEditing = !isUndefined(sponsor);

  const handleSubmit = async (data: {name: string, logo?: string}) => {
    if (isUndefined(sponsor)) {
      createSponsor(data);
    } else {
      editSponsor(sponsor.id, data);
    }
  };

  return (
    <Modal
      title={isEditing ? 'Edit Sponsor' : 'Add Sponsor'}
      onSubmit={handleSubmit}
      submitVerb={isEditing ? 'Modify' : 'Create'}
      submitColor={COLOR_POSITIVE}
      trigger={(
        <Button
          variant={isEditing ? 'soft' : 'solid'}
          color={isEditing ? COLOR_WARNING : COLOR_POSITIVE}
        >
          {isEditing ? 'Edit Sponsor' : 'Add Sponsor'}
        </Button>
      )}
      defaultValues={omit(sponsor, 'id')}
    >
      {(rhf) => <SponsorDataForm rhf={rhf} />}
    </Modal>
  );
}
