import {
  Button, Flex, Heading, Table,
} from '@radix-ui/themes';
import {
  TbDoorExit, TbPlusMinus, TbStar,
  TbUser,
} from 'react-icons/tb';
import { useTeamMembers } from '@/hooks/team';
import Entity from 'components/Entity';
import type { Team } from '@/types';
import { ErrorCallout, InfoCallout } from 'components/Callouts';
import AdminSidebar from 'components/AdminSidebar';
import RoleBadge from 'components/RoleBadge';
import AdminDataList from 'components/AdminDataList';
import { UserIcon } from '@/constants';

export default function TeamSidebar({ entity }: { entity: Team }) {
  const { data : members, error : membersError } = useTeamMembers(entity.id);

  return (
    <AdminSidebar title="Team Details">
      <AdminDataList data={{ ...entity }} />

      <Heading>Members</Heading>

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
            {members.map((member) => (
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
                  <Flex direction="row" align="center" justify="end" className="h-full *:!m-0">
                    <Button variant="ghost" color="red" disabled={member.role === 'captain'}>
                      <TbDoorExit />
                      Remove
                    </Button>
                    <Button variant="ghost" color="amber" disabled={member.role === 'captain'}>
                      <TbStar />
                      Assign Captain
                    </Button>
                  </Flex>
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table.Root>
      )}
      <Flex direction="row" gap="2" justify="between" align="center">
        <Heading>Activity</Heading>
        <Button variant="soft" color="amber">
          <TbPlusMinus />
          Point Adjust
        </Button>
      </Flex>
      <InfoCallout>
        Attempts, hint redemptions, and manual awards for this team.
      </InfoCallout>
      <Heading>Challenges</Heading>
      <InfoCallout>
        Deployed challenge instances for this team.
      </InfoCallout>
    </AdminSidebar>
  );
}
