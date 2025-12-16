import { EventIcon, TeamIcon, UserIcon } from '@/constants';
import { useTeamMembers } from '@/hooks/team';
import { useUserTeams, useUserWorkspace, useWorkspaceStatus } from '@/hooks/users';
import type { AdminUser, Team } from '@/types';
import { utf8ToBase64 } from '@/util';
import {
  Box,
  Flex,
  Grid,
  Heading,
  Table,
  Text,
} from '@radix-ui/themes';
import AdminSidebar from 'components/AdminSidebar';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import { ErrorCallout, WarningCallout } from 'components/Callouts';
import Entity from 'components/Entity';
import RoleBadge from 'components/RoleBadge';
import Statistic from 'components/Statistic';
import { useId } from 'react';
import AdminRegisterUserModal from './AdminRegisterUserModal';

import AdminUpdateUserModal from './AdminUpdateUserModal';
import BanUserModal from './BanUserModal';
import ImpersonateUserButton from './ImpersonateUserButton';
import RecycleWorkspaceModal from './RecycleWorkspaceModal';
import RestartWorkspaceModal from './RestartWorkspaceModal';
import UserVncModal from './UserVncModal';

function RegistrationRow({ userId, team }: { userId: number, team: Team }) {
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
        <Entity label={team.event_name || 'Unknown'} icon={EventIcon} to={`/admin/events?id=${team.event_id}`} />
      </Table.Cell>
      <Table.Cell>
        <Entity
          label={team.name}
          icon={TeamIcon}
          to={
            `/admin/teams?id=${team.id}&filter=${
              encodeURIComponent(utf8ToBase64(JSON.stringify({ event_name : { filterType : 'text', type : 'equals', filter : team.event_name } })))}`
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

export default function UserSidebar({ entity }: { entity: AdminUser }) {
  const { data : teamsData, error : teamsError } = useUserTeams(entity.id);
  const { data : workspaceData, error : workspaceError } = useUserWorkspace(entity.id);
  const { data : workspaceStatus, error : workspaceStatusError } = useWorkspaceStatus(entity.id);

  const headerId = useId();

  return (
    <AdminSidebar labelId={headerId}>
      <AdminSidebarHeader title={entity.name} icon={<UserIcon />} id={headerId}>
        <ImpersonateUserButton user={entity} />
        <BanUserModal user={entity} />
        <AdminUpdateUserModal user={entity} />
      </AdminSidebarHeader>

      {entity.banned && (<WarningCallout>This user is banned.</WarningCallout>)}

      <Grid columns="2" gap="4" align="center" justify="between">
        <Statistic
          label="Name"
          value={entity.name}
          size="5"
        />
        <Statistic
          label="ID"
          value={entity.id}
          size="5"
        />

        <Statistic
          label="Email"
          value={entity.email}
          size="5"
        />
        <Statistic
          label="Sponsor"
          value={entity.affiliation?.name || 'N/A'}
          size="5"
        />
        <Statistic
          label="Registered At"
          value={entity.registered_at.toLocaleString()}
          size="5"
        />
        <Box>
          <Text size="2" color="gray">Roles</Text>
          <Flex direction="row" wrap="wrap">
            {entity.roles.length === 0 && <Heading asChild size="5" weight="bold"><span>None</span></Heading>}
            {entity.roles.map((role) => (
              <RoleBadge key={role} value={role} size="2" />
            ))}
          </Flex>
        </Box>

      </Grid>

      <AdminSidebarHeader title="Registrations">
        <AdminRegisterUserModal userId={entity.id} />
      </AdminSidebarHeader>
      {teamsError && <ErrorCallout>{teamsError.message}</ErrorCallout> }
      {teamsData && (
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
            {teamsData.map((team) => (
              <RegistrationRow
                key={team.id}
                userId={entity.id}
                team={team}
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
              <UserVncModal userId={entity.id} />
            </Table.Cell>
          </Table.Row>
        </Table.Body>
      </Table.Root>
    </AdminSidebar>
  );
}
