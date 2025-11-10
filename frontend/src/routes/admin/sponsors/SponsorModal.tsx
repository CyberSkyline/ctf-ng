import Modal from '@/components/Modal'
import { COLOR_POSITIVE, COLOR_WARNING } from '@/constants'
import {
  Button,
  SegmentedControl,
  TextField
} from '@radix-ui/themes';
import FormField from 'components/FormField';
import FormDropdown from 'components/SelectDropdown';
import { useState } from 'react';
import { TbHeartHandshake } from 'react-icons/tb';
import NewLogoDropzone from './NewLogoDropzone';
import { createSponsor, editSponsor } from '@/hooks/sponsors';
import type { Sponsor } from '@/types';
import { isUndefined } from 'lodash';

export default function SponsorModal({sponsor}: {sponsor?: Sponsor}){
  const isEditing = !isUndefined(sponsor)
  const [ selectedOption, setSelectedOption ] = useState<'existing' | 'upload'>('existing');

  const handleSubmit = async (data: {name: string, logo?: string}) => {
    if(isUndefined(sponsor)){
      createSponsor(data)
    } else {
      editSponsor(sponsor.id, data)
    }
  }

  return (
    <Modal
      title={isEditing ? 'Edit Sponsor' : 'Add Sponsor'}
      onSubmit={handleSubmit}
      submitVerb={isEditing ? 'Modify' : 'Create'}
      submitColor={COLOR_POSITIVE}
      trigger={
        <Button
          variant={isEditing ? 'soft' : 'solid'}
          color={isEditing ? COLOR_WARNING : COLOR_POSITIVE }
        >
          {isEditing ? 'Edit Sponsor' : 'Add Sponsor'}
        </Button>
      }
      defaultValues={sponsor}
    >
      {({register, control, formState: { errors }}) => (
        <>
          <FormField label="Full Name" error={errors?.name}>
            {(injected) => (
              <TextField.Root
                type='text'
                {...register('name', {
                  required: 'Full Name is required'
                })}
                {...injected}
              />
            )}
          </FormField>

          <SegmentedControl.Root
            value={selectedOption}
            onValueChange={(val) => setSelectedOption(val as 'existing' | 'upload')}
          >
            <SegmentedControl.Item value='existing'>Use Exisiting Image</SegmentedControl.Item>
            <SegmentedControl.Item value='upload'>Upload New Image</SegmentedControl.Item>
          </SegmentedControl.Root>

          {selectedOption === 'existing' ? (
            <FormDropdown
              name='logo'
              label="Logo"
              options={[
                { name: 'cat', value: 'https://vgl.ucdavis.edu/sites/g/files/dgvnsk15116/files/media/images/Bengal%20cat.jpg', icon: <TbHeartHandshake /> },
                { name: 'dog', value: 'https://vgl.ucdavis.edu/sites/g/files/dgvnsk15116/files/media/images/shutterstock_334888937.jpg', icon: <TbHeartHandshake/> },
                { name: 'horse', value: 'https://vgl.ucdavis.edu/sites/g/files/dgvnsk15116/files/inline-images/Horse-Palomino-Cream-Dilution-Close-Crop-600px.jpg', icon: <TbHeartHandshake/> },
              ]}
              control={control}
              noneOption={false}
              placeholder='Select a logo...'
              value=''
              //error={errors.logo}
            />
          ) : (
            <NewLogoDropzone />
          )}

        </>
      )}
    </Modal>
  )
}