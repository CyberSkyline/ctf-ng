import {
  DeploymentIcon,
  EventIcon,
  TeamIcon,
  UserIcon,
} from '@/constants';
import { useTeam, useTeamMembers } from '@/hooks/team';
import { formatDate } from '@/util';
import {
  Flex,
  Grid,
  Skeleton,
  Table,
} from '@radix-ui/themes';
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
import SponsorBadge from './SponsorBadge';

export default function TeamSidebar({ selectedId }: { selectedId: number }) {
  const { data : team, error, isLoading : teamLoading } = useTeam(selectedId);
  const { data : members, error : membersError, isLoading : membersLoading } = useTeamMembers(selectedId);
  const headerId = useId();

  if (error) {
    return (
      <AdminSidebar labelId={headerId}>
        <ErrorCallout>{error.message}</ErrorCallout>
      </AdminSidebar>
    );
  }

  return (
    <AdminSidebar labelId={headerId}>
      <AdminSidebarHeader
        title={team?.name ?? 'Loading'}
        icon={<TeamIcon />}
        id={headerId}
        loading={teamLoading}
      >
        {team && (
          <>
            <AdminLink
              to="/admin/deployments"
              filter={{
                team_name : { filterType : 'text', type : 'equals', filter : team.name },
                event_name : { filterType : 'text', type : 'equals', filter : team.event_name },
              }}
              icon={DeploymentIcon}
              label="Deployments"
            />
            <AdminLink
              to="/admin/events"
              id={team.event_id}
              icon={EventIcon}
              label="Event"
            />
            <EditTeamModal teamToUpdate={team} />
          </>
        )}
      </AdminSidebarHeader>

      <Skeleton loading={teamLoading}>
        <Grid columns="2" gap="4" align="center" justify="between">
          <Statistic
            label="Name"
            value={team?.name ?? ''}
            size="5"
          />
          <Statistic
            label="ID"
            value={team?.id ?? ''}
            size="5"
          />

          <Statistic
            label="Event"
            value={team?.event_name ?? 'Unknown'}
            size="5"
          />
          <Statistic
            label="Invite Code"
            value={team?.invite_code ?? 'None'}
            size="5"
          />

          <Statistic
            label="Start Time"
            value={formatDate(team?.start_timestamp) || 'None'}
            size="5"
          />
          <Statistic
            label="End Time"
            value={formatDate(team?.end_time) || 'None'}
            size="5"
          />

          <Statistic
            label="Ranked"
            value={team?.ranked ? 'Yes' : 'No'}
            size="5"
          />
        </Grid>
      </Skeleton>

      <AdminSidebarHeader title="Members" />
      {membersError && <ErrorCallout>{membersError.message}</ErrorCallout> }
      {membersLoading && <Skeleton className="min-h-24" />}
      {members && (
        <Table.Root className="w-full">
          <Table.Header>
            <Table.Row>
              <Table.ColumnHeaderCell>Name</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Sponsor</Table.ColumnHeaderCell>
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
                <Table.Cell>{member.sponsor && <SponsorBadge sponsor={member.sponsor} />}</Table.Cell>
                <Table.Cell><RoleBadge value={member.role} /></Table.Cell>
                <Table.Cell>{formatDate(member.joined_at)}</Table.Cell>
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
        {team && <ScoreAdjustModal team={team} />}
      </AdminSidebarHeader>
      <TeamActivity eventId={team?.event_id ?? null} teamId={team?.id ?? null} />
    </AdminSidebar>
  );
}
