import { COLOR_POSITIVE, COLOR_WARNING } from '@/constants';
import { createSupportTag, putSupportTag } from '@/hooks/support';
import type { TicketTag } from '@/types';
import { Button, Flex, TextField } from '@radix-ui/themes';
import FormField from 'components/FormField';
import Modal from 'components/Modal';
import { isUndefined, omit } from 'lodash';

export default function CreateTagModal(
  { defaultValues }: {defaultValues?: TicketTag},
) {
  const isCreating = isUndefined(defaultValues);

  const handleSubmit = async (data: Omit<TicketTag, 'id' | 'ticket_count'>) => {
    if (isCreating) {
      return createSupportTag(data);
    }
    return putSupportTag(defaultValues?.id, data);
  };

  return (
    <Modal
      title={isCreating ? 'Create Support Tag' : 'Edit Support Tag'}
      description=""
      trigger={(
        <Button
          variant={isCreating ? 'solid' : 'soft'}
          color={isCreating ? COLOR_POSITIVE : COLOR_WARNING}
        >
          {isCreating ? 'Create Support Tag' : 'Edit Tag'}
        </Button>
      )}
      onSubmit={handleSubmit}
      submitVerb={isCreating ? 'Create' : 'Update'}
      defaultValues={omit(defaultValues, 'id', 'ticket_count')}
      requireTouchingForm
    >
      {({ register, formState : { errors } }) => (
        <>
          <Flex direction="row" gap="2" className="*:first:grow">
            <FormField label="Name" error={errors?.name}>
              {(injected) => (
                <TextField.Root
                  placeholder="Enter a tag name"
                  // eslint-disable-next-line react/jsx-props-no-spreading
                  {...register('name', {
                    required : 'Please enter a name.',
                  })}
                  // eslint-disable-next-line react/jsx-props-no-spreading
                  {...injected}
                />
              )}
            </FormField>
            <FormField label="Color" error={errors?.color}>
              {(injected) => (
                <input
                  type="color"
                  className="rounded"
                  // eslint-disable-next-line react/jsx-props-no-spreading
                  {...register('color', {
                    required : 'Please enter a color.',
                  })}
                  // eslint-disable-next-line react/jsx-props-no-spreading
                  {...injected}
                />
              )}
            </FormField>
          </Flex>
          <FormField label="Description" error={errors?.description}>
            {(injected) => (
              <TextField.Root
                placeholder="Enter a description"
                // eslint-disable-next-line react/jsx-props-no-spreading
                {...register('description', {
                  required : 'Please enter a description.',
                })}
                // eslint-disable-next-line react/jsx-props-no-spreading
                {...injected}
              />
            )}
          </FormField>
        </>
      )}
    </Modal>
  );
}
