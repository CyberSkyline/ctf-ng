import { COLOR_POSITIVE } from '@/constants';
import Modal from 'components/Modal';
import { TbPlus } from 'react-icons/tb';
import { Button, TextField } from '@radix-ui/themes';
import FormField from 'components/FormField';
import { createEvent } from '@/hooks/events';
import { useNavigate } from 'react-router';

export default function EventCreationModal() {
  const navigate = useNavigate();

  const handleSubmit = async (data: { name: string}) => {
    createEvent(data).then((eventId) => {
      navigate(`/admin/events?id=${eventId}&tab=details`);
    });
  };

  return (
    <Modal
      title="Create Event"
      trigger={(
        <Button variant="solid" color={COLOR_POSITIVE}>
          <TbPlus />
          Create Event
        </Button>
      )}
      onSubmit={handleSubmit}
      submitVerb="Create"
      submitColor={COLOR_POSITIVE}
    >
      {({ register, formState : { errors } }) => (
        <FormField label="Name" error={errors?.name}>
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
      )}
    </Modal>
  );
}
