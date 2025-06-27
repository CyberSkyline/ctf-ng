import {
  Flex, Heading, Spinner, Table,
} from '@radix-ui/themes';
import {
  TbUser,
  TbUsersGroup,
} from 'react-icons/tb';
import { useSearchParams } from 'react-router';
import { useTeam } from '@/hooks/team';
import { useUsers } from '@/hooks/users';
import Entity from 'components/Entity';
import type { TeamMember } from '@/types';
import { ErrorCallout } from 'components/Callouts';

function TeamMemberRow({ member }: { member: TeamMember}) {
  // Temporary lookup into all users since the useUser endpoint has not merged yet.
  const { data } = useUsers();
  return (
    <Table.Row>
      <Table.Cell>
        <Entity
          label={data?.users.find((u) => u.id === member.user_id)?.name ?? 'Unknown User'}
          to={`/admin/users?id=${member.user_id}`}
          icon={TbUser}
        />
      </Table.Cell>
      <Table.Cell>{member.role}</Table.Cell>
      <Table.Cell>{new Date(member.joined_at).toLocaleString()}</Table.Cell>
    </Table.Row>
  );
}

export default function TeamSidebar() {
  const [searchParams] = useSearchParams();
  const teamId = Number(searchParams.get('id'));

  const { data, error, isLoading } = useTeam(teamId);

  if (error) {
    return (
      <ErrorCallout>{error.message}</ErrorCallout>
    );
  }

  if (isLoading) {
    return (
      <Flex direction="column" align="center" justify="center" className="w-full h-full">
        <Spinner />
      </Flex>
    );
  }

  if (!teamId || !data) {
    return (
      <Flex direction="column" align="center" justify="center" className="w-full h-full">
        <TbUsersGroup className="text-(--gray-9) text-9xl" />
        <Heading className="text-(--gray-9)" size="4">
          Select a team to view details.
        </Heading>
      </Flex>
    );
  }

  return (
    <>
      <Heading>{data.team.name}</Heading>

      <Heading>Members</Heading>

      <Table.Root className="w-full">
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeaderCell>Name</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Role</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Joined</Table.ColumnHeaderCell>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {data.team_members.map((member) => (
            <TeamMemberRow key={member.user_id} member={member} />
          ))}
        </Table.Body>
      </Table.Root>

    </>
  );
}
