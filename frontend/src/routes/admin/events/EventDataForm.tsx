import type { Event } from '@/types';
import {
  Checkbox,
  Flex,
  TextArea,
  TextField,
} from '@radix-ui/themes';
import { Form } from 'radix-ui';

function adjustDateForInput(date: Date | null): string {
  // Adjust the date to be in the format required by datetime-local input
  if (date === null) return '';
  const dateObj = new Date(date);
  const offset = dateObj.getTimezoneOffset();
  const localDate = new Date(dateObj.getTime() - (offset * 60 * 1000));
  return localDate.toISOString().slice(0, 16);
}

export default function EventDataForm({
  initial,
}: {
  initial?: Omit<Event, 'id'>,
}) {
  return (
    <>
      <Form.Field name="Name">
        <Form.Label>Name</Form.Label>
        <Form.Control asChild>
          <TextField.Root
            name="name"
            defaultValue={initial?.name || ''}
            placeholder="Event Name"
            required
          />
        </Form.Control>
        <Form.Message match="valueMissing">
          Event name is required.
        </Form.Message>
      </Form.Field>

      <Form.Field name="description">
        <Form.Label>Description</Form.Label>
        <Form.Control asChild>
          <TextArea
            defaultValue={initial?.description || ''}
            placeholder="Event Description"
            rows={4}
            resize="vertical"
          />
        </Form.Control>
      </Form.Field>

      <Flex direction="row" gap="2" className="*:grow *:basis-0">
        <Form.Field name="registration_start_date">
          <Form.Label>Registration Opens</Form.Label>
          <Form.Control asChild>
            <TextField.Root
              type="datetime-local"
              onChange={(e) => { e.target.form?.reportValidity(); }}
              defaultValue={adjustDateForInput(initial?.registration_start_date || null)}
            />
          </Form.Control>
          <Form.Message match="badInput" />
        </Form.Field>
        <Form.Field name="registration_end_date">
          <Form.Label>Registration Closes</Form.Label>
          <Form.Control asChild>
            <TextField.Root
              type="datetime-local"
              onChange={(e) => { e.target.form?.reportValidity(); }}
              defaultValue={adjustDateForInput(initial?.registration_end_date || null)}
            />
          </Form.Control>
          <Form.Message match="badInput" />
        </Form.Field>
      </Flex>

      <Flex direction="row" gap="2" className="*:grow *:basis-0">
        <Form.Field name="start_time">
          <Form.Label>Event Starts</Form.Label>
          <Form.Control asChild>
            <TextField.Root
              type="datetime-local"
              defaultValue={adjustDateForInput(initial?.start_time || null)}
              required
            />
          </Form.Control>
          <Form.Message match="valueMissing" />
          <Form.Message match="badInput" />
        </Form.Field>

        <Form.Field name="end_time">
          <Form.Label>Event Ends</Form.Label>
          <Form.Control asChild>
            <TextField.Root
              type="datetime-local"
              name="end_time"
              defaultValue={adjustDateForInput(initial?.end_time || null)}
              required
            />
          </Form.Control>
          <Form.Message match="valueMissing" />
          <Form.Message match="badInput" />
        </Form.Field>
      </Flex>

      <Form.Field name="max_team_size">
        <Form.Label>Max Team Size</Form.Label>
        <Form.Control asChild>
          <TextField.Root
            type="number"
            defaultValue={initial?.max_team_size.toString() || '1'}
            min={1}
            max={8}
            required
          />
        </Form.Control>
        <Form.Message match="valueMissing" />
        <Form.Message match="rangeOverflow" />
        <Form.Message match="rangeUnderflow" />
      </Form.Field>

      <Flex direction="row" gap="2" className="*:grow *:basis-0 my-1" wrap="wrap">
        <Form.Field name="public" className="flex gap-1">
          <Form.Control asChild>
            <Checkbox
              defaultChecked={initial?.public}
              size="3"
            />
          </Form.Control>
          <Form.Label>Public</Form.Label>
        </Form.Field>
        <Form.Field name="locked" className="flex gap-1">
          <Form.Control asChild>
            <Checkbox defaultChecked={initial?.locked} size="3" />
          </Form.Control>
          <Form.Label>Disable Team Management</Form.Label>

        </Form.Field>
        <Form.Field name="registration_open" className="flex gap-1">
          <Form.Control asChild>
            <Checkbox
              defaultChecked={initial?.registration_open}
              size="3"
            />
          </Form.Control>
          <Form.Label>Registration Open</Form.Label>
        </Form.Field>
      </Flex>
    </>
  );
}
