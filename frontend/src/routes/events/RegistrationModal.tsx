import { registerMyEvent, registerMyEventTeamJoin } from '@/hooks/events';
import type { Event } from '@/types';
import {
  Box,
  Button,
  Checkbox,
  Flex,
  SegmentedControl,
  Text,
  TextField,
} from '@radix-ui/themes';
import { InfoCallout, WarningCallout } from 'components/Callouts';
import FormField from 'components/FormField';
import Modal from 'components/Modal';
import RadixMarkdown from 'components/RadixMarkdown';
import { isUndefined } from 'lodash';
import { useState } from 'react';
import { Controller } from 'react-hook-form';
import { TbArrowRight, TbPlus } from 'react-icons/tb';
import { useNavigate, useParams } from 'react-router';

export default function RegistrationModal({ eventId, eventName, isTeamGame }: {eventId : Event['id'], eventName: string, isTeamGame: boolean}) {
  const { inviteCode, idEvent } = useParams();
  const joinWithCode = !!(eventId === Number(idEvent) && !isUndefined(inviteCode));

  const [ selectedOption, setSelectedOption ] = useState<'create-team' | 'join-team'>(joinWithCode ? 'join-team' : 'create-team');

  const navigate = useNavigate();

  const handleRegister = async (data: { leaderboardName: string; joinCode: string; termsConditions: boolean }) => {
    if (selectedOption === 'join-team') {
      return registerMyEventTeamJoin(eventId, data.joinCode).then(() => {
        navigate(`/events/${eventId}`);
      });
    }

    const { leaderboardName } = data;
    return registerMyEvent(eventId, leaderboardName).then(() => {
      navigate(`/events/${eventId}`);
    });
  };

  function getDescription() {
    return isTeamGame ? 'Please do not use your real name or user name for your team name.'
      : 'Please do not use your real name for your leaderboard name.';
  }

  return (
    <Modal
      title={`Register for ${eventName}`}
      trigger={(
        <Button variant="soft">Register</Button>
      )}
      onSubmit={handleRegister}
      submitVerb="Register"
      defaultOpen={joinWithCode}
      defaultValues={{
        leaderboardName : '',
        joinCode : joinWithCode ? inviteCode : '',
        termsConditions : false,
      }}
      onOpenChange={(open) => {
        if (!open && joinWithCode) {
          // If the user closes the modal while registering via an invite link, take them back to the event page
          navigate('/events');
        }

        setSelectedOption('create-team');
      }}
    >
      {({ register, control, formState : { errors } }) => (
        <>
          {isTeamGame && (
            <SegmentedControl.Root
              value={selectedOption}
              onValueChange={(val) => setSelectedOption(val as 'create-team' | 'join-team')}
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

          { selectedOption === 'create-team' && (
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

          { (selectedOption === 'join-team') && (
            <>
              {!joinWithCode && (
                <InfoCallout>
                  Open an invite link provided by your team captain or enter the invite code below to join the team.
                </InfoCallout>
              )}
              <FormField label="Invite Code" error={errors?.joinCode}>
                {(injected) => (
                  <TextField.Root
                    readOnly={joinWithCode}
                    {...register('joinCode', {
                      required : {
                        value : true, message : 'An invite code is required to join an existing team',
                      },
                      minLength : {
                        value : 32, message : 'Invite code should be 32 characters',
                      },
                      maxLength : {
                        value : 32, message : 'Invite code should be 32 characters',
                      },
                    })}
                    {...injected}
                  />
                )}
              </FormField>
            </>
          )}

          <Box className="text-sm">
            <RadixMarkdown>
              {`I acknowledge that I have read and understand the [eligibility criteria](https://presidentscup.cisa.gov/pc7/#eligibility) and [contest rules](https://presidentscup.cisa.gov/pc7/#rules)
          for CISA's President's Cup Cybersecurity Competition. I agree to (1) comply with these criteria and rules and
          (2) accept all decisions made by CISA and the contest administrators regarding the competition.
          I will lodge all complaints or concerns I may have regarding the competition through my employer agency, which may submit them to CISA on my behalf.`}
            </RadixMarkdown>
          </Box>

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
                    id="termsConditions"
                    checked={field.value}
                    onCheckedChange={(checked) => field.onChange(checked)}
                    onBlur={field.onBlur}
                    ref={field.ref}
                  />
                  I agree to the Terms and Conditions
                </Flex>
              </Text>

            )}
          />

          {errors.termsConditions?.message && <WarningCallout>{errors.termsConditions.message.toString()}</WarningCallout>}
        </>
      )}

    </Modal>
  );
}
