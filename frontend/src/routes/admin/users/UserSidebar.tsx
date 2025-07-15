import {
  Button,
  Flex,
  Heading,
  Table,
} from '@radix-ui/themes';
import { TbPlus } from 'react-icons/tb';
import Entity from 'components/Entity';
import { ErrorCallout } from 'components/Callouts';
import { EventIcon, TeamIcon } from '@/constants';
import AdminDataList from 'components/AdminDataList';
import { useTeamMembers, useUserTeams } from '@/hooks/team';
import { useUserEvents } from '@/hooks/events';
import _ from 'lodash';
import type { Event, Team, User } from '@/types';
import AdminSidebar from 'components/AdminSidebar';
import RoleBadge from 'components/RoleBadge';

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
        <Entity label={team.name} icon={TeamIcon} to={`/admin/teams?event=${team.event_id}&id=${team.id}`} />
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

  const eventsMap = _.keyBy(eventsData, 'id');

  return (
    <AdminSidebar title="User Details">
      <AdminDataList data={{ ...entity }} />

      <Flex direction="row" gap="4" justify="between" align="center">
        <Heading>Registrations</Heading>
        <Button variant="soft">
          <TbPlus />
          Register
        </Button>
      </Flex>
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

      <Heading>Workspace</Heading>
    </AdminSidebar>
  );
}
