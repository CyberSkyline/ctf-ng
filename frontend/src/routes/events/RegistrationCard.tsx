import { useEventStatus, useMyEligibility } from '@/hooks/events';
import { useMySponsor, useRegistration } from '@/hooks/users';
import type { Event } from '@/types';
import {
  Box,
  Card,
  Flex,
  Link as RadixLink,
  Text,
} from '@radix-ui/themes';
import { ErrorCallout, WarningCallout } from 'components/Callouts';
import RequireEventPermission from 'components/RequireEventPermission';
import Statistic from 'components/Statistic';
import Timer from 'components/Timer';
import { isNil } from 'lodash';
import { Link } from 'react-router';
import { mutate } from 'swr';
import LeaveTeamModal from './LeaveTeamModal';
import RegistrationModal from './RegistrationModal';
import RenameTeamModal from './RenameTeamModal';

export default function RegistrationCard({ event }: {event: Event}) {
  const {
    isRegistered, isUnregistered, team, isLoading, error,
  } = useRegistration(event.id);
  const { isConcluded } = useEventStatus(event.id);

  const isIndividual = event.max_team_size === 1;

  // don't check eligibility if already registered since we know it will fail
  const { data : eligibility, error : eligibilityError } = useMyEligibility(isUnregistered ? event.id : null);
  const { data : mySponsor, error : mySponsorError } = useMySponsor();

  if (isLoading) return null; // don't show anything while loading
  if (isUnregistered && !eligibility && !eligibilityError) return null; // if not eligible, don't show registration
  if (mySponsorError) return null; // Users must have a sponsor on their profile to register for events
  if (event.locked) return null; // Don't allow registration if event is locked

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  if (isUnregistered && eligibilityError) {
    return <ErrorCallout>{eligibilityError.message}</ErrorCallout>;
  }

  return (
    <>
      <Card className="!flex flex-col gap-3">
        {isRegistered && (
        <>
          <Statistic
            label={`You ${isConcluded ? 'were' : 'are'} registered ${!isIndividual ? 'on team' : 'as'}:`}
            value={`${team!.name}`}
            size="6"
          />
          {team?.end_time && (
            <Box>
              <Text color="gray" size="2">Time remaining:</Text>
              <Timer
                target={new Date(team.end_time)}
                onEnd={() => {
                  // Refresh SWR state on timer end
                  mutate(`/permissions/${event.id}/me`);
                  mutate(`/events/${event.id}/me/team`);
                  mutate(`/users/me/teams`);
                }}
              />
            </Box>
          )}
          <Flex direction="row" gap="4" align="center" className="empty:!hidden">
            <RequireEventPermission eventId={event.id} permission="CAN_LEAVE_TEAM" permissionDeniedPlaceholder={null}>
              <LeaveTeamModal event={event} />
            </RequireEventPermission>
            <RequireEventPermission eventId={event.id} permission="CAN_EDIT_TEAM" permissionDeniedPlaceholder={null}>
              <RenameTeamModal event={event} />
            </RequireEventPermission>
          </Flex>
        </>
        )}
        { isUnregistered && eligibility && !eligibilityError && (
        <>
          <Text>You are not registered for this event.</Text>
          <Flex direction="row" gap="4" align="center">
            {isNil(mySponsor)
              ? (
                <WarningCallout>
                  You must select a sponsor on the
                  {' '}
                  <RadixLink asChild>
                    <Link to="/profile?sponsor=1">profile page</Link>
                  </RadixLink>
                  {' '}
                  prior to registering for events.
                </WarningCallout>
              )
              : <RegistrationModal eventId={event.id} eventName={event.name} isTeamGame={event.max_team_size > 1} />}
          </Flex>
        </>
        )}
      </Card>
      {team?.member_count === 1 && event.max_team_size > 1 && (
        <WarningCallout>
          Your team only has one member. You will not be able to participate in this event until more members join your team.
        </WarningCallout>
      )}
    </>
  );
}
