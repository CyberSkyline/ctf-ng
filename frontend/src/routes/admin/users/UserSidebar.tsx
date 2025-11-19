import { EventIcon, TeamIcon, UserIcon } from '@/constants';
import { useTeamMembers } from '@/hooks/team';
import {
  useUserEvents,
  useUserTeams,
  useUserWorkspace,
  useWorkspaceStatus,
} from '@/hooks/users';
import type { Event, Team, User } from '@/types';
import { utf8ToBase64 } from '@/util';
import { Table } from '@radix-ui/themes';
import AdminDataList from 'components/AdminDataList';
import AdminSidebar from 'components/AdminSidebar';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import { ErrorCallout } from 'components/Callouts';
import Entity from 'components/Entity';
import RoleBadge from 'components/RoleBadge';
import { keyBy } from 'lodash';
import AdminRegisterUserModal from './AdminRegisterUserModal';
import ImpersonateUserButton from './ImpersonateUserButton';
import RecycleWorkspaceModal from './RecycleWorkspaceModal';
import RestartWorkspaceModal from './RestartWorkspaceModal';

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
          to={
            `/admin/teams?id=${team.id}&filter=${
              encodeURIComponent(utf8ToBase64(JSON.stringify({ event_name : { filterType : 'text', type : 'equals', filter : event.name } })))}`
          }
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
  const { data : workspaceData, error : workspaceError } = useUserWorkspace(entity.id);
  const { data : workspaceStatus, error : workspaceStatusError } = useWorkspaceStatus(entity.id);

  const eventsMap = keyBy(eventsData, 'id');

  return (
    <AdminSidebar>
      <AdminSidebarHeader title={entity.name} icon={<UserIcon />}>
        <ImpersonateUserButton user={entity} />
      </AdminSidebarHeader>

      <AdminDataList data={{ ...entity }} />

      <AdminSidebarHeader title="Registrations">
        <AdminRegisterUserModal userId={entity.id} />
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
      {workspaceError && <ErrorCallout>{workspaceError.message}</ErrorCallout> }
      {workspaceStatusError && <ErrorCallout>{workspaceStatusError.message}</ErrorCallout> }
      <Table.Root>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeaderCell>Id</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Host Ip</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Docker Id</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Status</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell align="right">Actions</Table.ColumnHeaderCell>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          <Table.Row key={workspaceData?.id}>
            <Table.Cell>
              { workspaceData?.id }
            </Table.Cell>
            <Table.Cell>
              { workspaceData?.hostip }
            </Table.Cell>
            <Table.Cell>
              { workspaceData?.dockerid }
            </Table.Cell>
            <Table.Cell>
              { workspaceStatus }
            </Table.Cell>
            <Table.Cell align="right">
              <RestartWorkspaceModal userId={entity.id} />
              <RecycleWorkspaceModal userId={entity.id} />
            </Table.Cell>
          </Table.Row>
        </Table.Body>
      </Table.Root>
    </AdminSidebar>
  );
}
