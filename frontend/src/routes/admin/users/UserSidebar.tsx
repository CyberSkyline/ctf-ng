import {
  Flex, Heading, Spinner, Table,
} from '@radix-ui/themes';
import {
  TbUser,
  TbUsersGroup,
} from 'react-icons/tb';
import { useSearchParams } from 'react-router';
import { useUserTeams } from '@/hooks/team';
import { useUsers } from '@/hooks/users';
import Entity from 'components/Entity';
import { ErrorCallout } from 'components/Callouts';
import { EventIcon } from '@/constants';
import AdminDataList from 'components/AdminDataList';

export default function UserSidebar() {
  const [searchParams] = useSearchParams();

  const userId = Number(searchParams.get('id'));

  // Temporary lookup into all users since the useUser endpoint has not merged yet.
  const { data : allUsers, error, isLoading } = useUsers();
  const data = allUsers?.users.find((u) => u.id === userId);

  const { data : teamData, error : teamError, isLoading : teamLoading } = useUserTeams(userId);

  if (isLoading) {
    return <Spinner />;
  }

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  if (!userId || !data) {
    return (
      <Flex direction="column" align="center" justify="center" className="w-full h-full">
        <TbUser className="text-(--gray-9) text-9xl" />
        <Heading className="text-(--gray-9)" size="4">
          Select a user to view details.
        </Heading>
      </Flex>
    );
  }

  return (
    <>
      <Heading>{data.name}</Heading>
      <AdminDataList data={data} />
      <Heading>Registrations</Heading>
      {teamError && <ErrorCallout>{teamError.message}</ErrorCallout> }
      {teamLoading && <Spinner />}
      {teamData && (
        <Table.Root>
          <Table.Header>
            <Table.Row>
              <Table.ColumnHeaderCell>Event</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Team</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Joined At</Table.ColumnHeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {/* Need consistent serialization from the backend for types to match here - these should really be TeamMember objects */}
            {teamData?.teams.map((team) => (
              <Table.Row key={team.id}>
                <Table.Cell>
                  <Entity label={team.event_name} icon={EventIcon} to={`/admin/events?id=${team.event_id}`} />
                </Table.Cell>
                <Table.Cell>
                  <Entity label={team.team_name} icon={TbUsersGroup} to={`/admin/teams?event=${team.event_id}&id=${team.team_id}`} />
                </Table.Cell>
                <Table.Cell>
                  {new Date(team.joined_at).toLocaleString()}
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table.Root>
      )}
    </>
  );
}
