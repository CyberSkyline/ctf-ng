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

  const handleSubmit = async ({ event, team }: {event: string, team: string}) => {
    const eventId = +event;

    if (!eventId) {
      throw new Error('No event selected');
    }

    if (!team) {
      throw new Error('No team selected');
    }

    // a new team's name is wrapped in quotes so it can't be mistaken for a real invite code
    const newTeamMatch = team.match(/^"([\s\S]*)"$/);

    if (newTeamMatch) {
      const newTeamName = newTeamMatch[1];

      if (!newTeamName) {
        throw new Error('No team name provided');
      }

      return adminRegisterEvent(eventId, userId, newTeamName);
    }

    return adminRegisterEventTeamJoin(eventId, userId, team);
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
          team : '',
        }
      }
    >
      {({
        control, watch, formState : { errors }, setValue,
      }) => {
        const currentEvent = watch('event');
        const currentTeam = watch('team');
        const selectedEvent: Event | null = eventsMap[currentEvent] || null;

        if (currentEvent !== lastEventRef.current) {
          lastEventRef.current = currentEvent;

          // a quoted new team name isn't tied to the previous event, so it's fine to keep
          if (!currentTeam.startsWith('"')) {
            setValue('team', '');
          }
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
                name="team"
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
                createFreeformItem={(input) => ({ invite_code : `"${input}"`, name : String(input) })}
                placeholder="Search or create a team..."
                rules={
                  { required : 'Team is required.' }
                }
                error={errors.team}
              />
            )}
          </>
        );
      }}
    </Modal>
  );
}
