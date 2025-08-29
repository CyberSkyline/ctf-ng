import Modal from 'components/Modal';
import { Button, TextField } from '@radix-ui/themes';
import { Form } from 'radix-ui';
import { createSupportTag, putSupportTag } from '@/hooks/support';
import type { TicketTag } from '@/types';
import { isUndefined } from 'lodash';
import { COLOR_POSITIVE, COLOR_WARNING } from '@/constants';

export default function CreateTagModal(
  { defaultValues }: {defaultValues?: TicketTag},
) {
  const handleSubmit = async (data: FormData) => {
    const entries = Object.fromEntries(data.entries());
    const newTag: Omit<TicketTag, 'id | ticket_count'> = {
      name : entries.name as string,
      color : entries.color as string,
      description : entries.description as string,
    };

    if (isUndefined(defaultValues)) {
      return createSupportTag(newTag);
    }
    return putSupportTag(defaultValues?.id, newTag);
  };

  return (
    <Modal
      title={isUndefined(defaultValues) ? 'Create Support Tag' : 'Edit Support Tag'}
      description=""
      trigger={(
        <Button
          variant={isUndefined(defaultValues) ? 'solid' : 'soft'}
          color={isUndefined(defaultValues) ? COLOR_POSITIVE : COLOR_WARNING}
        >
          {isUndefined(defaultValues) ? 'Create Support Tag' : 'Edit Tag'}
        </Button>
      )}
      onSubmit={handleSubmit}
      submitVerb={isUndefined(defaultValues) ? 'Create' : 'Update'}
      requireTouchingForm
    >
      <Form.Field name="name">
        <Form.Label>Name</Form.Label>
        <Form.Control asChild>
          <TextField.Root
            defaultValue={defaultValues?.name}
            placeholder="Enter a tag name"
            required
          />
        </Form.Control>
        <Form.Message match="valueMissing">
          Please enter a name.
        </Form.Message>
      </Form.Field>
      <Form.Field name="color">
        <Form.Label>Hex Color</Form.Label>
        <Form.Control asChild>
          <TextField.Root
            defaultValue={defaultValues?.color}
            placeholder="Enter a hex color"
          />
        </Form.Control>
        <Form.Message match="valueMissing">
          Please enter a name.
        </Form.Message>
      </Form.Field>
      <Form.Field name="description">
        <Form.Label>Description</Form.Label>
        <Form.Control asChild>
          <TextField.Root
            defaultValue={defaultValues?.description}
            placeholder="Enter a description"
          />
        </Form.Control>
        <Form.Message match="valueMissing">
          Please enter a name.
        </Form.Message>
      </Form.Field>
    </Modal>
  );
}
