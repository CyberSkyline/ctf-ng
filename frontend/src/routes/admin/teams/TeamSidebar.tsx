import {
  DeploymentIcon,
  EventIcon,
  TeamIcon,
  UserIcon,
} from '@/constants';
import { useTeamMembers } from '@/hooks/team';
import type { Team } from '@/types';
import { Flex, Grid, Table } from '@radix-ui/themes';
import AdminLink from 'components/AdminLink';
import AdminSidebar from 'components/AdminSidebar';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import { ErrorCallout } from 'components/Callouts';
import Entity from 'components/Entity';
import RoleBadge from 'components/RoleBadge';
import Statistic from 'components/Statistic';
import { useId } from 'react';
import EditTeamModal from './EditTeamModal';
import KickUserModal from './KickUserModal';
import PromoteUserModal from './PromoteUserModal';
import ScoreAdjustModal from './ScoreAdjustModal';
import TeamActivity from './TeamActivity';

export default function TeamSidebar({ entity }: { entity: Team }) {
  const { data : members, error : membersError } = useTeamMembers(entity.id);
  const headerId = useId();

  return (
    <AdminSidebar labelId={headerId}>
      <AdminSidebarHeader title={entity.name} icon={<TeamIcon />} id={headerId}>
        <AdminLink
          to="/admin/deployments"
          filter={{
            team_name : { filterType : 'text', type : 'equals', filter : entity.name },
            event_name : { filterType : 'text', type : 'equals', filter : entity.event_name },
          }}
          icon={DeploymentIcon}
          label="Deployments"
        />
        <AdminLink
          to="/admin/events"
          id={entity.event_id}
          icon={EventIcon}
          label="Event"
        />
        <EditTeamModal teamToUpdate={entity} />
      </AdminSidebarHeader>

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
          label="Event"
          value={entity.event_name || 'Unknown'}
          size="5"
        />
        <Statistic
          label="Invite Code"
          value={entity.invite_code || 'None'}
          size="5"
        />

        <Statistic
          label="Start Time"
          value={entity.start_timestamp?.toLocaleString() || 'None'}
          size="5"
        />
        <Statistic
          label="End Time"
          value={entity.end_time?.toLocaleString() || 'None'}
          size="5"
        />

        <Statistic
          label="Ranked"
          value={entity.ranked ? 'Yes' : 'No'}
          size="5"
        />
      </Grid>

      <AdminSidebarHeader title="Members" />
      {membersError && <ErrorCallout>{membersError.message}</ErrorCallout> }
      {members && (
        <Table.Root className="w-full">
          <Table.Header>
            <Table.Row>
              <Table.ColumnHeaderCell>Name</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Role</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Joined</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell />
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {members.sort((a, b) => a.user_name.localeCompare(b.user_name)).map((member) => (
              <Table.Row key={member.id}>
                <Table.Cell>
                  <Entity
                    label={member.user_name}
                    to={`/admin/users?id=${member.user_id}`}
                    icon={UserIcon}
                  />
                </Table.Cell>
                <Table.Cell><RoleBadge value={member.role} /></Table.Cell>
                <Table.Cell>{member.joined_at.toLocaleString()}</Table.Cell>
                <Table.Cell>
                  <Flex direction="row" align="center" gap="4" justify="end">
                    <KickUserModal member={member} solo={members.length === 1} />
                    <PromoteUserModal member={member} />
                  </Flex>
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table.Root>
      )}

      <AdminSidebarHeader title="Activity">
        <ScoreAdjustModal team={entity} />
      </AdminSidebarHeader>
      <TeamActivity eventId={entity.event_id} teamId={entity.id} />
    </AdminSidebar>
  );
}
