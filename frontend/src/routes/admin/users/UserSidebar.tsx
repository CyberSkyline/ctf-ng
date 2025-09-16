import {
  COLOR_POSITIVE,
  EventIcon,
  TeamIcon,
  UserIcon,
} from '@/constants';
import { useTeamMembers } from '@/hooks/team';
import { useUserEvents, useUserTeams } from '@/hooks/users';
import type { Event, Team, User } from '@/types';
import { Button, Table } from '@radix-ui/themes';
import AdminDataList from 'components/AdminDataList';
import AdminSidebar from 'components/AdminSidebar';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import { ErrorCallout } from 'components/Callouts';
import Entity from 'components/Entity';
import RoleBadge from 'components/RoleBadge';
import { keyBy } from 'lodash';
import { TbPlus } from 'react-icons/tb';

function RegistrationRow({ userId, team, event }: { userId: number, team: Team, event: Event }) {
  const { data : teamMembers } = useTeamMembers(team.id);
  if (!teamMembers) {
    return null;
  }

  const membership = teamMembers.find((member) => member.user_id === userId);
  if (!membership) {
    return null;
  }

  return (
    <Table.Row key={team.id}>
      <Table.Cell>
        <Entity label={event.name} icon={EventIcon} to={`/admin/events?id=${event.id}`} />
      </Table.Cell>
      <Table.Cell>
        <Entity
          label={team.name}
          icon={TeamIcon}
          to={`/admin/teams?id=${team.id}&filter=${btoa(JSON.stringify({ event_name : { filterType : 'text', type : 'equals', filter : event.name } }))}`}
        />
      </Table.Cell>
      <Table.Cell>
        <RoleBadge value={membership.role} />
      </Table.Cell>
      <Table.Cell>
        {membership?.joined_at.toLocaleString()}
      </Table.Cell>
    </Table.Row>
  );
}

export default function UserSidebar({ entity }: { entity: User }) {
  const { data : teamsData, error : teamsError } = useUserTeams(entity.id);
  const { data : eventsData, error : eventsError } = useUserEvents(entity.id);

  const eventsMap = keyBy(eventsData, 'id');

  return (
    <AdminSidebar>
      <AdminSidebarHeader title={entity.name} icon={<UserIcon />} />

      <AdminDataList data={{ ...entity }} />

      <AdminSidebarHeader title="Registrations">
        <Button variant="soft" color={COLOR_POSITIVE}>
          <TbPlus />
          Register
        </Button>
      </AdminSidebarHeader>
      {teamsError && <ErrorCallout>{teamsError.message}</ErrorCallout> }
      {eventsError && <ErrorCallout>{eventsError.message}</ErrorCallout> }
      {teamsData && eventsData && (
        <Table.Root>
          <Table.Header>
            <Table.Row>
              <Table.ColumnHeaderCell>Event</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Team</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Role</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Joined</Table.ColumnHeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {teamsData?.map((team) => (
              <RegistrationRow
                key={team.id}
                userId={entity.id}
                team={team}
                event={eventsMap[team.event_id]}
              />
            ))}
          </Table.Body>
        </Table.Root>
      )}

      <AdminSidebarHeader title="Workspace" />
    </AdminSidebar>
  );
}
