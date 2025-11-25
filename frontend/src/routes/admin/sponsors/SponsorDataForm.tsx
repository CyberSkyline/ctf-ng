import { SegmentedControl, TextField } from '@radix-ui/themes';
import FormField from 'components/FormField';
import FormDropdown from 'components/SelectDropdown';
import { useState } from 'react';
import { useFileList, useFileUrl } from '@/hooks/fileuploads';
import type { Sponsor } from '@/types';
import { chain } from 'lodash';
import type { UseFormReturn } from 'react-hook-form';
import { ErrorCallout } from 'components/Callouts';
import NewLogoDropzone from './NewLogoDropzone';

export default function SponsorDataForm({
  rhf,
}: {
  rhf: UseFormReturn<Omit<Sponsor, 'id'>>,
}) {
  const {
    register, control, formState : { errors }, watch, setValue,
  } = rhf;
  const selectedImage = watch('logo');

  const { data : imagePreview, error : imageError } = useFileUrl('sponsor-logos', selectedImage);

  const [ selectedOption, setSelectedOption ] = useState<'existing' | 'upload'>('existing');

  const { data, error : listError } = useFileList('sponsor-logos');
  const options = chain(data?.files)
    .filter((file) => file.filename !== '')
    .map(({ filename }) => ({ name : filename, value : filename }))
    .value() || [];

  return (
    <>
      <FormField label="Full Name" error={errors?.name}>
        {(injected) => (
          <TextField.Root
            type="text"
            {...register('name', {
              required : 'Full Name is required',
            })}
            {...injected}
          />
        )}
      </FormField>

      <SegmentedControl.Root
        value={selectedOption}
        onValueChange={(val) => setSelectedOption(val as 'existing' | 'upload')}
      >
        <SegmentedControl.Item value="existing">Use Exisiting Image</SegmentedControl.Item>
        <SegmentedControl.Item value="upload">Upload New Image</SegmentedControl.Item>
      </SegmentedControl.Root>

      {selectedOption === 'existing' ? (
        <>
          {listError && <ErrorCallout>{listError.message}</ErrorCallout>}
          {imageError && <ErrorCallout>{imageError.message}</ErrorCallout>}
          <FormDropdown
            name="logo"
            label="Logo"
            options={options}
            control={control}
            noneOption={false}
            placeholder="Select a logo..."
            value=""
          />
          {imagePreview && <img src={imagePreview.url} alt={imagePreview.filename} />}
        </>
      ) : (
        <NewLogoDropzone setValue={setValue} />
      )}
    </>
  );
}
