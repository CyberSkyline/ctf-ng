import { COLOR_NEGATIVE, COLOR_WARNING, UserIcon } from '@/constants';
import { useTeamMembers } from '@/hooks/team';
import type { Team } from '@/types';
import {
  Button,
  Flex,
  Heading,
  Table,
} from '@radix-ui/themes';
import AdminDataList from 'components/AdminDataList';
import AdminSidebar from 'components/AdminSidebar';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import { ErrorCallout, InfoCallout } from 'components/Callouts';
import Entity from 'components/Entity';
import RoleBadge from 'components/RoleBadge';
import { TbDoorExit, TbPackages, TbStar } from 'react-icons/tb';
import { Link } from 'react-router';

export default function TeamSidebar({ entity }: { entity: Team }) {
  const { data : members, error : membersError } = useTeamMembers(entity.id);

  return (
    <AdminSidebar>
      <AdminSidebarHeader title="Team Details">
        <Button variant="soft" color={COLOR_INFO} asChild>
          <Link to={`/admin/deployments?filter=${btoa(JSON.stringify({ team : { filterType : 'number', type : 'equals', filter : entity.id } }))}`}>
            <TbPackages />
            Deployments
          </Link>
        </Button>
      </AdminSidebarHeader>
      <AdminDataList data={{ ...entity }} />

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
                    <Button variant="ghost" color={COLOR_NEGATIVE} disabled={member.role === 'captain'}>
                      <TbDoorExit />
                      Remove
                    </Button>
                    <Button variant="ghost" color={COLOR_WARNING} disabled={member.role === 'captain'}>
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
      <AdminSidebarHeader title="Activity">
        <Button variant="soft" color="amber">
          <TbPlusMinus />
          Point Adjust
        </Button>
      </AdminSidebarHeader>
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
