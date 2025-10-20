import { COLOR_POSITIVE } from '@/constants';
import { adminRegisterEvent, adminRegisterEventTeamJoin, useAllEvents } from '@/hooks/events';
import { useAllTeams } from '@/hooks/team';
import { useUserTeams } from '@/hooks/users';
import type { Event } from '@/types';
import { Button, TextField } from '@radix-ui/themes';
import { ErrorCallout, WarningCallout } from 'components/Callouts';
import FormField from 'components/FormField';
import Modal from 'components/Modal';
import FormDropdown from 'components/SelectDropdown';
import { keyBy } from 'lodash';
import { TbPlus } from 'react-icons/tb';

export default function AdminRegisterUserModal({ userId }: {userId: number}) {
  const { data : events, error, isLoading } = useAllEvents();
  const { data : userTeams, error : userTeamsError, isLoading : userTeamsLoading } = useUserTeams(userId);

  const userEventIds = new Set(userTeams?.map((e) => e.event_id) || []);

  const filteredEvents = events?.filter((event) => !userEventIds.has(event.id)) || [];

  const eventsMap = keyBy(filteredEvents, 'id');

  const { data : teams, error : teamsError, isLoading : teamsLoading } = useAllTeams();

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
          loading={isLoading || userTeamsLoading || teamsLoading}
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
          joinCode : 'new',
          teamName : '',
        }
      }
    >
      {({
        register, control, watch, formState : { errors }, setValue,
      }) => {
        const selectedEvent: Event | null = eventsMap[watch('event')] || null;
        const selectedTeam = watch('joinCode');

        const filteredTeams = teams && selectedEvent ? teams.filter((t) => t.event_id.toString() === selectedEvent.id.toString()) : [];

        if (selectedTeam !== 'new' && !filteredTeams.map((t) => t.invite_code).includes(selectedTeam)) {
          // if we've switched to a different event and the selected team is no longer valid, reset to 'new'
          setValue('joinCode', 'new');
        }

        return (
          <>
            {error && <ErrorCallout>{error.message}</ErrorCallout>}
            {userTeamsError && <ErrorCallout>{userTeamsError.message}</ErrorCallout>}
            {teamsError && <ErrorCallout>{teamsError.message}</ErrorCallout>}
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
            {selectedEvent && selectedEvent.max_team_size > 1 && (
              <FormDropdown
                name="joinCode"
                label="Team"
                options={
                  [
                    { name : 'Create new...', value : 'new' },
                    ...filteredTeams?.map((team) => ({
                      name : `${team.name} (${team.member_count}/${selectedEvent.max_team_size})`,
                      value : team.invite_code!,
                    })) || [],
                  ]
                }
                control={control}
                noneOption={false}
                value="new"
                placeholder={watch('event') && selectedEvent.max_team_size > 1 ? 'Select team...' : 'N/A (individual event)'}
                rules={
                  { required : 'Team is required.' }
                }
                error={errors.joinCode}
                disabled={!watch('event')}
              />
            )}
            {selectedEvent && selectedTeam === 'new'
            && (
            <FormField label="Team Name" error={errors.teamName}>
              {(injected) => (
                <TextField.Root
                  {...register('teamName', { required : selectedTeam === 'new' ? 'Team name is required.' : false })}
                  placeholder="Team Name"
                  {...injected}
                />
              )}
            </FormField>
            )}

          </>
        );
      }}
    </Modal>
  );
}
