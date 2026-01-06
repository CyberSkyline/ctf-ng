import type { Event } from '@/types';
import { adjustDateForInput } from '@/util';
import { COLOR_POSITIVE } from '@/constants';
import { useState } from 'react';
import { useForm } from 'react-hook-form'
import { omit } from 'lodash'
import Dropzone from 'react-dropzone';
import { TbUpload } from 'react-icons/tb';
import { Button, Flex, TextField, TextArea, DataList } from '@radix-ui/themes';
import EventGraphic from 'components/EventGraphic';
import RadixMarkdown from 'components/RadixMarkdown';
import FormField from 'components/FormField';
import FormDropdown from 'components/SelectDropdown';
import { ErrorCallout } from 'components/Callouts';
import ActionButtonsGroup from './ActionButtonsGroup';
import { directUpload, useFileList, useFileUrl } from '@/hooks/fileuploads';

export default function EventDetailsTab({ event }: { event: Event }) {
  const {
    control,
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue,
    setError,
    clearErrors,
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

  const currentImage = watch('image');
  const { data: gameCards, error: gameCardsError, isLoading: gameCardsLoading } = useFileList('event-cards');
  const { data: fileUrl, error: fileUrlError } = useFileUrl('event-cards', currentImage === 'None' ? '' : currentImage || '');

  const [uploading, setUploading] = useState(false);
  const [isEditing, setIsEditing] = useState<boolean>(true)

  const update = async (data: Event) => {
    // This is going to end up being a PUT
    console.log('update', data)
  }

  const onDrop = async (acceptedFiles: File[]) => {
    const formData = new FormData();
    formData.append('folder', 'event-cards');
    formData.append('file', acceptedFiles[0]);

    setUploading(true);

    clearErrors('image');
    directUpload(formData).then((data) => {
      setValue('image', data.filename);
    }).catch((err) => setError('image', { message: err.message }))
      .finally(() => setUploading(false));
  };

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
          <FormField label="Name" error={errors.name}>
            {(injected) => (
              <TextField.Root
                placeholder="Event Name"
                {...register('name', {
                  required: 'Event name is required',
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

          <Flex direction="row" gap="2" className="[&>*:first-child]:grow">
            <FormDropdown
              name="image"
              label="Image"
              options={gameCards ? gameCards.files.filter((file) => file.filename.length > 0).map((file) => ({
                name: file.filename,
                value: file.filename,
              })) : []}
              disabled={gameCardsLoading || !!gameCardsError}
              error={errors.image}
              rules={{
                required: 'Image is required',
              }}
              control={control}
            />
            <FormField label="Upload">
              {() => (
                <Dropzone
                  accept={{
                    'image/png': ['.png'],
                    'image/jpeg': ['.jpeg'],
                  }}
                  multiple={false}
                  onDrop={onDrop}
                  disabled={uploading}
                >
                  {({
                    getRootProps, getInputProps,
                  }) => (
                    <Button
                      {...getRootProps()}
                      color={COLOR_POSITIVE}
                      loading={uploading}
                      variant="soft"
                      type="button"
                    >
                      <input {...getInputProps()} />
                      <TbUpload aria-label="Upload" />
                    </Button>
                  )}
                </Dropzone>
              )}
            </FormField>
          </Flex>

          {fileUrl && <img src={fileUrl?.download_url} alt="Selected Event" className="max-h-48 object-contain bg-(--gray-1) rounded" />}
          {fileUrlError && (<ErrorCallout>{fileUrlError.message}</ErrorCallout>)}

          <ActionButtonsGroup
            isEditing={isEditing}
            setIsEditing={setIsEditing}
            reset={reset}
          />
        </form>
      ) : (
        <DataList.Root>
          <DataList.Item>
            <DataList.Label>Name</DataList.Label>
            <DataList.Value>{event.name}</DataList.Value>
          </DataList.Item>

          <DataList.Item>
            <DataList.Label>Description</DataList.Label>
            <DataList.Value>
              <RadixMarkdown>
                {event.description || ''}
              </RadixMarkdown>
            </DataList.Value>
          </DataList.Item>

          <DataList.Item>
            <DataList.Label>Logo</DataList.Label>
            <DataList.Value>
              <EventGraphic event={event} className="w-64 rounded-lg shadow-lg" />
            </DataList.Value>
          </DataList.Item>
        </DataList.Root>
      )}

    </Flex>
  );
}
