import { COLOR_POSITIVE, COLOR_WARNING } from '@/constants';
import { createEvent, updateEvent } from '@/hooks/events';
import type { Event } from '@/types';
import { Button } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { omit } from 'lodash';
import type { DefaultValues } from 'react-hook-form';
import { TbPencil, TbPlus } from 'react-icons/tb';
import { adjustDateForInput } from '@/util';
import EventDataForm from './EventDataForm';

export default function EventModal({
  eventToUpdate,
}: {
  eventToUpdate?: Event;
}) {
  const handleSubmit = async (data: Omit<Event, 'id'>) => {
    if (eventToUpdate) {
      // Update existing event
      return updateEvent(eventToUpdate.id, data);
    }

    return createEvent(data);
  };

  // Default value Dates must be converted to datetime-local string format, even though the value is typed as Date.
  // This is because valueAsDate only applies to entered values, not default values.
  const defaultValues: DefaultValues<Omit<Event, 'id'>> = {
    ...omit(eventToUpdate, 'id'),
    registration_start_date : adjustDateForInput(eventToUpdate?.registration_start_date || null) as unknown as Date,
    registration_end_date : adjustDateForInput(eventToUpdate?.registration_end_date || null) as unknown as Date,
    start_time : adjustDateForInput(eventToUpdate?.start_time || null) as unknown as Date,
    end_time : adjustDateForInput(eventToUpdate?.end_time || null) as unknown as Date,
  };

  return (
    <Modal
      title={eventToUpdate ? 'Edit Event' : 'Create Event'}
      trigger={
        eventToUpdate
          ? (
            <Button variant="soft" color={COLOR_WARNING}>
              <TbPencil />
              Edit
            </Button>
          )
          : (
            <Button variant="solid" color={COLOR_POSITIVE}>
              <TbPlus />
              Create Event
            </Button>
          )
      }
      onSubmit={handleSubmit}
      submitVerb={eventToUpdate ? 'Update' : 'Create'}
      submitColor={eventToUpdate ? COLOR_WARNING : COLOR_POSITIVE}
      defaultValues={defaultValues}
    >
      {(rhf) => <EventDataForm rhf={rhf} />}
    </Modal>
  );
}
