import {
  Box,
  Checkbox,
  Flex,
  SegmentedControl,
  Text,
  TextField,
} from '@radix-ui/themes';
import { ErrorCallout, InfoCallout, WarningCallout } from 'components/Callouts';
import FormField from 'components/FormField';
import RadixMarkdown from 'components/RadixMarkdown';
import { Controller, type UseFormReturn, useWatch } from 'react-hook-form';
import { TbArrowRight, TbPlus } from 'react-icons/tb';
import { useTeamNameFromCode } from '@/hooks/events';
import { useState, useEffect } from 'react';
import { useParams } from 'react-router';

export default function RegistrationDataForm({
  rhf,
  isTeamGame,
  joinWithCode,
  eventId,
}: {
  rhf: UseFormReturn<{ leaderboardName: string; joinCode: string; termsConditions: boolean, selectedOption: string }>,
  isTeamGame: boolean,
  joinWithCode: boolean,
  eventId: number,
}) {
  const {
    register, control, formState : { errors }, setValue,
  } = rhf;
  const { inviteCode } = useParams();

  const selectedOption = useWatch({ control, name : 'selectedOption' });

  const inviteCodeWatched = useWatch({ control, name : 'joinCode' });
  const [ debouncedCode, setDebouncedCode ] = useState<string | undefined>();

  const { data, error } = useTeamNameFromCode(eventId, debouncedCode);

  useEffect(() => {
    if (inviteCode) {
      setValue('joinCode', inviteCode);
      setDebouncedCode(inviteCode);
    }
  }, [ inviteCode, setValue ]);

  useEffect(() => {
    if (!inviteCodeWatched) {
      setDebouncedCode(undefined);
      return;
    }

    const timeout = setTimeout(() => {
      const joinCode = inviteCodeWatched.indexOf('/') > -1 ? inviteCodeWatched.substring(inviteCodeWatched.lastIndexOf('/') + 1) : inviteCodeWatched;
      setDebouncedCode(joinCode);
    }, 500);

    // eslint-disable-next-line consistent-return
    return () => clearTimeout(timeout);
  }, [ inviteCodeWatched ]);

  function getDescription() {
    return isTeamGame ? 'Please do not use your real name or user name for your team name.'
      : 'Please do not use your real name for your leaderboard name.';
  }

  return (
    <>
      {isTeamGame && (
        <Controller
          control={control}
          name="selectedOption"
          render={({ field }) => (
            <SegmentedControl.Root
              value={field.value}
              onValueChange={(val) => field.onChange(val as 'create-team' | 'join-team')}
              className="!h-16"
            >
              <SegmentedControl.Item value="create-team">
                <TbPlus className="text-2xl mx-auto" />
                Create New Team
              </SegmentedControl.Item>
              <SegmentedControl.Item value="join-team">
                <TbArrowRight className="text-2xl mx-auto" />
                Join Existing Team
              </SegmentedControl.Item>
            </SegmentedControl.Root>
          )}
        />
      )}

      {selectedOption === 'create-team' && (
        <>
          <WarningCallout>{getDescription()}</WarningCallout>
          <FormField label={isTeamGame ? 'Team Name' : 'Leaderboard Name'} error={errors?.leaderboardName}>
            {(injected) => (
              <TextField.Root
                placeholder={isTeamGame ? 'Enter your team name' : 'Enter your leaderboard name'}
                {...register('leaderboardName', {
                  required : {
                    value : true, message : 'This field is required',
                  },
                  maxLength : {
                    value : 100, message : 'Name must be at most 100 characters',
                  },
                })}
                {...injected}
              />
            )}
          </FormField>
        </>
      )}

      {(selectedOption === 'join-team') && (
        <>
          {!joinWithCode && (
            <InfoCallout>
              Open an invite link provided by your team captain or enter the invite code below to join the team.
            </InfoCallout>
          )}
          {error
            && <ErrorCallout>{error.message}</ErrorCallout>}
          <FormField label="Invite Code" error={errors?.joinCode}>
            {(injected) => (
              <TextField.Root
                readOnly={joinWithCode}
                {...register('joinCode', {
                  required : {
                    value : true, message : 'An invite code is required to join an existing team',
                  },
                })}
                {...injected}
              />
            )}
          </FormField>
          {data && (
          <p>
            <b>Team: </b>
            {data.name}
          </p>
          )}
        </>
      )}

      <Box className="text-sm">
        <RadixMarkdown>
          {`I acknowledge that I have read and understand the
          [eligibility criteria](https://presidentscup.cisa.gov/pc7/#eligibility)
          and [contest rules](https://presidentscup.cisa.gov/pc7/#rules)
          for CISA's President's Cup Cybersecurity Competition. I agree to (1) comply with these criteria and rules and
          (2) accept all decisions made by CISA and the contest administrators regarding the competition.
          I will lodge all complaints or concerns I may have regarding the competition through my employer agency, which may submit them to CISA on my behalf.`}
        </RadixMarkdown>
      </Box>

      <FormField label={null} error={errors?.termsConditions}>
        {(injected) => (
          <Controller
            control={control}
            name="termsConditions"
            rules={{
              required : {
                value : true, message : 'You must accept the terms and conditions to register',
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
                  I agree to the Terms and Conditions
                </Flex>
              </Text>
            )}
          />
        )}
      </FormField>
    </>
  );
}
