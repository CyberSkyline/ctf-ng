import { COLOR_POSITIVE } from '@/constants';
import { startMyTeam, useEventStatus } from '@/hooks/events';
import { useRegistration } from '@/hooks/users';
import type { Event } from '@/types';
import {
  Box,
  Button,
  Checkbox,
  Flex,
  Strong,
  Text,
} from '@radix-ui/themes';
import { InfoCallout, WarningCallout } from 'components/Callouts';
import FormField from 'components/FormField';
import Modal from 'components/Modal';
import RequireEventPermission from 'components/RequireEventPermission';
import { useEffect, useState } from 'react';
import { Controller, type FieldError } from 'react-hook-form';
import { TbPlayerPlay } from 'react-icons/tb';

export default function StartModal({ event }: {event: Event}) {
  const { isOngoing } = useEventStatus(event.id);
  const { team } = useRegistration(event.id);
  const isTeam = event.max_team_size > 1;

  const handleStart = async () => startMyTeam(event.id);

  const [ availableMinutes, setAvailableMinutes ] = useState<number | null>(null);

  // Calculate available time every 5 seconds
  useEffect(() => {
    const updateAvailableMinutes = () => {
      let avail = null;
      if (event.time_limit_minutes) {
        avail = event.time_limit_minutes;

        if (event.end_time) {
          const minutesUntilEnd = Math.round((new Date(event.end_time).getTime() - Date.now()) / 60000);
          if (minutesUntilEnd < avail) {
            // the event will end before the full time limit elapses - truncate the calculated available time to match backend
            // clamp to 0 if negative, just in case
            avail = Math.max(minutesUntilEnd, 0);
          }
        }
      }
      setAvailableMinutes(avail);
    };

    const intervalId = setInterval(updateAvailableMinutes, 5000);
    updateAvailableMinutes(); // calculate time immediately on mount

    return () => clearInterval(intervalId);
  });

  const formattedTimeLimit = availableMinutes
    ? new Intl.DurationFormat('en', { style : 'long' })
      .format({
        hours : Math.floor(availableMinutes / 60),
        minutes : availableMinutes % 60,
      })
    : null;

  return (
    <RequireEventPermission
      eventId={event.id}
      permission="CAN_START_TEAM_TIMER"
      permissionDeniedPlaceholder={isOngoing
        ? (
          <Text size="3" color="gray">
            {(team?.member_count === 1 && isTeam)
              ? `Your team must have at least two members to start.`
              : 'Waiting for your team captain to start the event.'}
          </Text>
        )
        : null}
    >
      <Box>
        <Text size="3" color="gray">
          When
          {' '}
          {isTeam ? 'your team is' : 'you are'}
          {' '}
          ready to start the event, press the start button below.
        </Text>
      </Box>
      <Modal
        trigger={(
          <Button color={COLOR_POSITIVE} className="pulsate">
            <TbPlayerPlay />
            Start Event
          </Button>
        )}
        title="Start Event"
        description={`Are you sure you want to start ${event.name}?`}
        submitVerb="Start"
        submitColor={COLOR_POSITIVE}
        onSubmit={handleStart}
      >
        {({ control, formState : { errors } }) => (
          <>
            {isTeam && (
              <WarningCallout>
                <Strong>Team members may not join or leave the team once you have started.</Strong>
                <br />
                Please ensure that all members are present and ready before starting.
              </WarningCallout>
            )}
            {availableMinutes !== event.time_limit_minutes && (
              <InfoCallout>
                <Strong>
                  This event will end before
                  {' '}
                  {isTeam ? 'your team\'s' : 'your'}
                  {' '}
                  allotted time can elapse.
                </Strong>
                <br />
                Your timer will be truncated.
                {' '}
                {isTeam ? 'Your team' : 'You'}
                {' '}
                will only have until the event&apos;s scheduled end time to work.
              </InfoCallout>
            )}
            <FormField label={null} error={errors?.acknowledge as FieldError}>
              {(injected) => (
                <Controller
                  control={control}
                  name="acknowledge"
                  rules={{
                    required : {
                      value : true, message : `Please confirm that ${isTeam ? 'your team is' : 'you are'} ready to start`,
                    },
                  }}
                  defaultValue={false}
                  render={({ field }) => (
                    <Text as="label" size="2">
                      <Flex gap="2">
                        <Checkbox
                          checked={field.value}
                          onCheckedChange={(checked) => field.onChange(checked)}
                          onBlur={field.onBlur}
                          ref={field.ref}
                          {...injected}
                        />
                        <Text>
                          Yes,
                          {' '}
                          {isTeam ? 'my team is' : 'I am'}
                          {' '}
                          ready to start
                          {' '}
                          {event.name}
                          .
                          {formattedTimeLimit && (
                          <>
                            <br />
                            I understand that
                            {' '}
                            {isTeam ? 'my team' : 'I'}
                            {' '}
                            will have
                            {' '}
                            <Strong>
                              {formattedTimeLimit}
                            </Strong>
                            {' '}
                            to work on challenges and this timer will begin as soon as I press start below.
                          </>
                          )}
                        </Text>
                      </Flex>
                    </Text>
                  )}
                />
              )}
            </FormField>
          </>
        )}
      </Modal>
    </RequireEventPermission>
  );
}
