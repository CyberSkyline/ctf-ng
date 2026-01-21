import type { Event } from '@/types';
import { COLOR_POSITIVE } from '@/constants';
import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { omit } from 'lodash';
import Dropzone from 'react-dropzone';
import { TbUpload } from 'react-icons/tb';
import {
  Button,
  Flex,
  TextField,
  TextArea,
  DataList,
} from '@radix-ui/themes';
import EventGraphic from 'components/EventGraphic';
import RadixMarkdown from 'components/RadixMarkdown';
import FormField from 'components/FormField';
import FormDropdown from 'components/SelectDropdown';
import { ErrorCallout } from 'components/Callouts';
import { directUpload, useFileList, useFileUrl } from '@/hooks/fileuploads';
import { updateEvent } from '@/hooks/events';
import ActionButtonsGroup from './ActionButtonsGroup';

export default function EventDetailsTab({ event }: { event: Event }) {
  const {
    control,
    register,
    handleSubmit,
    formState : { errors },
    watch,
    setValue,
    setError,
    clearErrors,
    reset,
  } = useForm<Event>({
    defaultValues : {
      ...omit(event, 'id'),
      image : event?.image || 'None',
    },
  });

  useEffect(() => {
    reset({
      ...omit(event, 'id'),
      image : event?.image || 'None',
    });
  }, [ event, reset ]);

  const currentImage = watch('image');
  const { data : gameCards, error : gameCardsError, isLoading : gameCardsLoading } = useFileList('event-cards');
  const { data : fileUrl, error : fileUrlError } = useFileUrl('event-cards', currentImage === 'None' ? '' : currentImage || '');

  const [ uploading, setUploading ] = useState(false);
  const [ isEditing, setIsEditing ] = useState<boolean>(false);
  const [ loading, setLoading ] = useState<boolean>(false);
  const [ updateError, setUpdateError ] = useState<string| null>(null);

  const update = async (data: Event) => {
    setLoading(true);
    setUpdateError(null);

    const updatingEvent = data;

    if (updatingEvent.image === 'None') {
      updatingEvent.image = null;
    }

    updateEvent(event.id, updatingEvent).then(() => {
      setIsEditing(false);
      reset(data);
    }).catch((err) => {
      setUpdateError(err.message);
    }).finally(() => {
      setLoading(false);
    });
  };

  const onDrop = async (acceptedFiles: File[]) => {
    const formData = new FormData();
    formData.append('folder', 'event-cards');
    formData.append('file', acceptedFiles[0]);

    setUploading(true);

    clearErrors('image');
    directUpload(formData).then((data) => {
      setValue('image', data.filename);
    }).catch((err) => setError('image', { message : err.message }))
      .finally(() => setUploading(false));
  };

  const buttonControls = () => (
    <ActionButtonsGroup
      isEditing={isEditing}
      setIsEditing={setIsEditing}
      reset={() => {
        reset();
        setUpdateError(null);
      }}
      loading={loading}
      formId="eventDetailsForm"
    />
  );

  return (
    <Flex direction="column" gap="3" className="mb-4">
      {buttonControls()}

      {isEditing ? (
        <form
          id="eventDetailsForm"
          onSubmit={handleSubmit(update)}
          className="space-y-4"
        >
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

          <Flex direction="row" gap="2" className="[&>*:first-child]:grow">
            <FormDropdown
              name="image"
              label="Image"
              options={gameCards ? gameCards.files.filter((file) => file.filename.length > 0).map((file) => ({
                name : file.filename,
                value : file.filename,
              })) : []}
              disabled={gameCardsLoading || !!gameCardsError}
              error={errors.image}
              rules={{
                required : 'Image is required',
              }}
              control={control}
            />
            <FormField label="Upload">
              {() => (
                <Dropzone
                  accept={{
                    'image/png' : [ '.png' ],
                    'image/jpeg' : [ '.jpeg' ],
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

          {updateError && (<ErrorCallout>{updateError}</ErrorCallout>)}
          {buttonControls()}
        </form>
      ) : (
        <DataList.Root>
          <DataList.Item>
            <DataList.Label>Name</DataList.Label>
            <DataList.Value>{event.name}</DataList.Value>
          </DataList.Item>

          <DataList.Item>
            <DataList.Label>Description</DataList.Label>
            <DataList.Value className="flex-col">
              <RadixMarkdown>
                {event.description || ''}
              </RadixMarkdown>
            </DataList.Value>
          </DataList.Item>

          <DataList.Item>
            <DataList.Label>Image</DataList.Label>
            <DataList.Value>
              <EventGraphic event={event} className="w-64 rounded-lg shadow-lg" />
            </DataList.Value>
          </DataList.Item>
        </DataList.Root>
      )}

    </Flex>
  );
}
