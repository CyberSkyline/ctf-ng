import { createEvent, updateEvent } from '@/hooks/events';
import type { Event } from '@/types';
import { Button } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbPencil, TbPlus } from 'react-icons/tb';
import EventDataForm from './EventDataForm';

export default function EventModal({
  eventToUpdate,
}: {
  eventToUpdate?: Event;
}) {
  const handleSubmit = async (data: FormData) => {
    const entries = Object.fromEntries(data.entries());
    const event: Omit<Event, 'id'> = {
      name : entries.name as string,
      description : entries.description as string,
      start_time : new Date(entries.start_time as string),
      end_time : new Date(entries.end_time as string),
      locked : entries.locked === 'on',
      public : entries.public === 'on',
      max_team_size : Number(entries.max_team_size),
      registration_open : entries.registration_open === 'on',
      registration_start_date : new Date(entries.registration_start_date as string),
      registration_end_date : new Date(entries.registration_end_date as string),
    };

    if (eventToUpdate) {
      // Update existing event
      return updateEvent(eventToUpdate.id, event);
    }

    return createEvent(event);
  };

  return (
    <Modal
      title={eventToUpdate ? 'Edit Event' : 'Create Event'}
      trigger={
        eventToUpdate
          ? (
            <Button variant="soft" color="amber">
              <TbPencil />
              Edit
            </Button>
          )
          : (
            <Button variant="solid" color="lime">
              <TbPlus />
              Create Event
            </Button>
          )
      }
      onSubmit={handleSubmit}
      submitVerb={eventToUpdate ? 'Update' : 'Create'}
      submitColor={eventToUpdate ? 'amber' : 'lime'}
      requireTouchingForm={!!eventToUpdate}
    >
      <EventDataForm initial={eventToUpdate} />
    </Modal>
  );
}
