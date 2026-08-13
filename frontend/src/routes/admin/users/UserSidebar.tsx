import {
  COLOR_NEGATIVE,
  COLOR_POSITIVE,
  EventIcon,
  TeamIcon,
  UserIcon,
} from '@/constants';
import { useTeamMembers } from '@/hooks/team';
import {
  useUser,
  useUserTeams,
  useUserWorkspace,
  useWorkspaceStatus,
} from '@/hooks/users';
import type { Team } from '@/types';
import { formatDate, utf8ToBase64 } from '@/util';
import {
  Badge,
  Box,
  Flex,
  Grid,
  Heading,
  Table,
  Text,
  Tooltip,
} from '@radix-ui/themes';
import AdminSidebar from 'components/AdminSidebar';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import { ErrorCallout, InfoCallout, WarningCallout } from 'components/Callouts';
import Entity from 'components/Entity';
import RoleBadge from 'components/RoleBadge';
import Statistic from 'components/Statistic';
import { upperCase } from 'lodash';
import { useId } from 'react';
import AdminRegisterUserModal from './AdminRegisterUserModal';

import AdminUpdateUserModal from './AdminUpdateUserModal';
import BanUserModal from './BanUserModal';
import ImpersonateUserButton from './ImpersonateUserButton';
import RecycleWorkspaceModal from './RecycleWorkspaceModal';
import RestartWorkspaceModal from './RestartWorkspaceModal';
import UserVncModal from './UserVncModal';
import DeleteWorkspaceModal from './DeleteWorkspaceModal';

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
        {formatDate(membership?.joined_at)}
      </Table.Cell>
    </Table.Row>
  );
}

export default function UserSidebar({ selectedId }: { selectedId: number }) {
  const { data : user, error : userError } = useUser(selectedId);
  const { data : teamsData, error : teamsError } = useUserTeams(selectedId);
  const { data : workspaceData, error : workspaceError } = useUserWorkspace(selectedId);
  const { data : workspaceStatus, error : workspaceStatusError } = useWorkspaceStatus(selectedId);

  const headerId = useId();

  if (userError) return <ErrorCallout>{userError.message}</ErrorCallout>;
  if (!user) return null;

  return (
    <AdminSidebar labelId={headerId}>
      <AdminSidebarHeader title={user.name} icon={<UserIcon />} id={headerId}>
        <ImpersonateUserButton user={user} />
        <BanUserModal user={user} />
        <AdminUpdateUserModal user={user} />
      </AdminSidebarHeader>

      {user.banned && (<WarningCallout>This user is banned.</WarningCallout>)}

      <Grid columns="2" gap="4" align="center" justify="between">
        <Statistic
          label="Name"
          value={user.name}
          size="5"
        />
        <Statistic
          label="ID"
          value={user.id}
          size="5"
        />

        <Statistic
          label="Email"
          value={user.email}
          size="5"
        />
        <Statistic
          label="Sponsor"
          value={user.affiliation?.name || 'N/A'}
          size="5"
        />
        <Statistic
          label="Registered At"
          value={formatDate(user.registered_at)}
          size="5"
        />
        <Box>
          <Text size="2" color="gray">Roles</Text>
          <Flex direction="row" wrap="wrap">
            {user.roles.length === 0 && <Heading asChild size="5" weight="bold"><span>None</span></Heading>}
            {user.roles.map((role) => (
              <RoleBadge key={role} value={role} size="2" />
            ))}
          </Flex>
        </Box>

      </Grid>

      <AdminSidebarHeader title="Registrations">
        <AdminRegisterUserModal userId={user.id} />
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
                userId={user.id}
                team={team}
              />
            ))}
          </Table.Body>
        </Table.Root>
      )}

      <AdminSidebarHeader title="Workspace" />
      {workspaceError
        && (workspaceError.message.includes('Workspace not found')
          ? <InfoCallout>This user does not have a workspace.</InfoCallout>
          : <ErrorCallout>{workspaceError.message}</ErrorCallout>
        ) }
      {workspaceData && (
        <>
          { workspaceStatusError && (
            <ErrorCallout>
              Failed to get workspace status.
              <br />
              {workspaceStatusError.message}
            </ErrorCallout>
          ) }
          <Table.Root>
            <Table.Header>
              <Table.Row>
                <Table.ColumnHeaderCell>ID</Table.ColumnHeaderCell>
                <Table.ColumnHeaderCell>Status</Table.ColumnHeaderCell>
                <Table.ColumnHeaderCell>Docker ID</Table.ColumnHeaderCell>
                <Table.ColumnHeaderCell>Host IP</Table.ColumnHeaderCell>
                <Table.ColumnHeaderCell align="right">Actions</Table.ColumnHeaderCell>
              </Table.Row>
            </Table.Header>
            <Table.Body>
              <Table.Row key={workspaceData.id}>
                <Table.Cell>
                  { workspaceData.id }
                </Table.Cell>
                <Table.Cell>
                  <Badge color={workspaceStatus === 'running' ? COLOR_POSITIVE : COLOR_NEGATIVE} role="status">
                    {upperCase(workspaceStatus || 'unknown')}
                  </Badge>
                </Table.Cell>
                <Table.Cell>
                  <Tooltip content={<Text>{workspaceData.dockerid}</Text>}>
                    <Text>{workspaceData.dockerid.slice(0, 12)}</Text>
                  </Tooltip>
                </Table.Cell>
                <Table.Cell>
                  { workspaceData.hostip }
                </Table.Cell>
                <Table.Cell align="right">
                  <Flex direction="row" justify="end" gap="4">
                    <UserVncModal userId={user.id} />
                    <RestartWorkspaceModal userId={user.id} />
                    <RecycleWorkspaceModal userId={user.id} />
                    <DeleteWorkspaceModal userId={user.id} />
                  </Flex>
                </Table.Cell>
              </Table.Row>
            </Table.Body>
          </Table.Root>
        </>
      )}
    </AdminSidebar>
  );
}
