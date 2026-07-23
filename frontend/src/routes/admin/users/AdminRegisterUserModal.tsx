import { COLOR_POSITIVE } from '@/constants';
import { adminRegisterEvent, adminRegisterEventTeamJoin, useAllEvents } from '@/hooks/events';
import useAdminGridDatasource from '@/hooks/grid';
import { useUserTeams } from '@/hooks/users';
import type { Event, Team } from '@/types';
import { Button } from '@radix-ui/themes';
import { ErrorCallout, WarningCallout } from 'components/Callouts';
import FormSearchField from 'components/FormSearchField';
import Modal from 'components/Modal';
import FormDropdown from 'components/SelectDropdown';
import { keyBy } from 'lodash';
import { useRef } from 'react';
import { TbPlus } from 'react-icons/tb';

export default function AdminRegisterUserModal({ userId }: {userId: number}) {
  const { data : events, error, isLoading } = useAllEvents();
  const { data : userTeams, error : userTeamsError, isLoading : userTeamsLoading } = useUserTeams(userId);

  const userEventIds = new Set(userTeams?.map((e) => e.event_id) || []);

  const filteredEvents = events?.filter((event) => !userEventIds.has(event.id)) || [];

  const eventsMap = keyBy(filteredEvents, 'id');

  const teamsDatasource = useAdminGridDatasource<Team>('/admin/teams')!;

  const lastEventRef = useRef('');

  const handleSubmit = async ({ event, joinCode, teamName }: {event: string, joinCode: string, teamName: string}) => {
    const eventId = +event;

    if (!eventId) {
      throw new Error('No event selected');
    }

    if (!joinCode) {
      throw new Error('No team selected');
    }

    if (joinCode === 'new') {
      if (!teamName) {
        throw new Error('No team name provided');
      }

      return adminRegisterEvent(eventId, userId, teamName);
    }

    // selectedTeam is a join code
    return adminRegisterEventTeamJoin(eventId, userId, joinCode);
  };

  return (
    <Modal
      title="Register User"
      description="Manually register this user for an event."
      trigger={(
        <Button
          variant="soft"
          color={COLOR_POSITIVE}
          loading={isLoading || userTeamsLoading}
        >
          <TbPlus />
          Register
        </Button>
      )}
      onSubmit={handleSubmit}
      submitVerb="Register"
      defaultValues={
        {
          event : '',
          joinCode : '',
          teamName : '',
        }
      }
    >
      {({
        control, watch, formState : { errors }, setValue,
      }) => {
        const currentEvent = watch('event');
        const selectedEvent: Event | null = eventsMap[currentEvent] || null;

        if (currentEvent !== lastEventRef.current) {
          // the previously selected team belongs to a different event
          lastEventRef.current = currentEvent;
          setValue('joinCode', '');
          setValue('teamName', '');
        }

        return (
          <>
            {error && <ErrorCallout>{error.message}</ErrorCallout>}
            {userTeamsError && <ErrorCallout>{userTeamsError.message}</ErrorCallout>}
            <WarningCallout>
              Always ensure that the user has agreed to the rules and eligibility criteria of the event before registering them.
            </WarningCallout>

            <FormDropdown
              name="event"
              label="Event"
              options={
              filteredEvents?.map((event) => ({
                name : event.name,
                value : event.id.toString(),
              })) || []
            }
              control={control}
              noneOption={false}
              placeholder="Select event..."
              rules={
                { required : 'Event is required.' }
              }
              value=""
              error={errors.event}
            />
            {selectedEvent && (
              <FormSearchField
                name="joinCode"
                label="Team"
                control={control}
                datasource={teamsDatasource}
                valueKey="invite_code"
                labelKey="name"
                getSublabel={(team) => `${team.member_count}/${selectedEvent.max_team_size}`}
                staticFilter={{
                  event_name : { filterType : 'text', type : 'equals', filter : selectedEvent.name },
                  // only teams with an open slot are joinable
                  member_count : { filterType : 'number', type : 'lessThan', filter : selectedEvent.max_team_size },
                }}
                createFreeformItem={(input) => {
                  setValue('teamName', String(input));
                  return { invite_code : 'new', name : String(input) };
                }}
                placeholder="Search or create a team..."
                rules={
                  { required : 'Team is required.' }
                }
                error={errors.joinCode}
              />
            )}
          </>
        );
      }}
    </Modal>
  );
}
