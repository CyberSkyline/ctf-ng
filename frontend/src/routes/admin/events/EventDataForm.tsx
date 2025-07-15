import type { Event } from '@/types';
import {
  Button,
  Checkbox,
  Flex,
  TextArea,
  TextField,
} from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import { Form } from 'radix-ui';
import { useState } from 'react';

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
  onSubmit,
  error,
}: {
  initial?: Omit<Event, 'id'>,
  onSubmit?: (event: Omit<Event, 'id'>) => void,
  error?: string
}) {
  // allow reset/submit only if the form has been touched
  // these buttons being enabled indicates unsaved changes
  const [ canReset, setCanReset ] = useState(false);

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setCanReset(false);
    const formData = new FormData(e.target as HTMLFormElement);

    const {
      name,
      description,
      start_time : startTime,
      end_time : endTime,
      locked : isLocked,
      public : isPublic,
      max_team_size : maxTeamSize,
      registration_open : isOpen,
      registration_start_date : openTime,
      registration_end_date : closeTime,
    } = Object.fromEntries(formData.entries());

    return onSubmit?.({
      name : name as string,
      description : description as string,
      start_time : new Date(startTime as string),
      end_time : new Date(endTime as string),
      locked : isLocked === 'on',
      public : isPublic === 'on',
      max_team_size : Number(maxTeamSize),
      registration_open : isOpen === 'on',
      registration_start_date : new Date(openTime as string),
      registration_end_date : new Date(closeTime as string),
    });
  }

  return (
    <Form.Root
      className="flex flex-col gap-2"
      onSubmitCapture={(e) => handleSubmit(e)}
      onChange={() => {
        setCanReset(true);
      }}
      onReset={() => {
        setCanReset(false);
      }}
    >
      { error && (
        <ErrorCallout>
          {error}
        </ErrorCallout>
      ) }
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
          <Form.Label>Locked</Form.Label>

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

      <Flex direction="row-reverse" gap="2">
        <Form.Submit asChild>
          <Button
            type="submit"
            disabled={!canReset}
          >
            {initial ? 'Save' : 'Create '}
          </Button>
        </Form.Submit>
        <Button
          variant="soft"
          type="reset"
          color="gray"
          disabled={!canReset}
        >
          {initial ? 'Revert' : 'Clear'}
        </Button>
      </Flex>
    </Form.Root>
  );
}
