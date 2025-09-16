import {
  COLOR_INFO,
  EventIcon,
  TeamIcon,
  UserIcon,
} from '@/constants';
import { useDeploymentServices } from '@/hooks/container';
import type { Deployment } from '@/types';
import {
  Button,
  Code,
  Skeleton,
  Table,
} from '@radix-ui/themes';
import AdminDataList from 'components/AdminDataList';
import AdminSidebar from 'components/AdminSidebar';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import { ErrorCallout, WarningCallout } from 'components/Callouts';
import Entity from 'components/Entity';
import { Link } from 'react-router';
import ServiceRow from './ServiceRow';

export default function DeploymentSidebar({ entity }: {entity: Deployment}) {
  const { data : serviceData, error } = useDeploymentServices(entity.challenge_id, entity.team_id);

  return (
    <AdminSidebar>
      <AdminSidebarHeader title="Deployment Details">
        <Button variant="soft" color={COLOR_INFO} asChild>
          <Link to={`/admin/teams?id=${entity.team_id}`}>
            <TeamIcon />
            Team
          </Link>
        </Button>
        <Button variant="soft" color={COLOR_INFO} asChild>
          <Link to={`/admin/events?id=${entity.event_id}`}>
            <EventIcon />
            Event
          </Link>
        </Button>
      </AdminSidebarHeader>
      <AdminDataList
        data={{
          team : entity.team_name,
          challenge : entity.challenge_name,
        }}
      />

      <AdminSidebarHeader title="Services" />
      {error && <ErrorCallout>{error.message}</ErrorCallout>}
      <Skeleton loading={!serviceData}>
        <Table.Root>
          <Table.Header>
            <Table.Row>
              <Table.ColumnHeaderCell>Name</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Status</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>ID</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Image</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Host IP</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell align="right">Actions</Table.ColumnHeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            { serviceData?.map((service) => (
              <ServiceRow key={service.id} service={service} />
            )) }
          </Table.Body>
        </Table.Root>
      </Skeleton>

      <AdminSidebarHeader title="Variables" />
      <WarningCallout>Not yet implemented.</WarningCallout>
      <Table.Root>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeaderCell>Variable</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Value</Table.ColumnHeaderCell>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          <Table.Row>
            <Table.Cell><Code color="gray">PASSWORD</Code></Table.Cell>
            <Table.Cell>abcdefghijkl</Table.Cell>
          </Table.Row>
          <Table.Row>
            <Table.Cell><Code color="gray">SOMETHING</Code></Table.Cell>
            <Table.Cell>something</Table.Cell>
          </Table.Row>
        </Table.Body>
      </Table.Root>

      <AdminSidebarHeader title="Workspaces" />
      <WarningCallout>Not yet implemented.</WarningCallout>
      <Table.Root>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeaderCell>User</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Address</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Actions</Table.ColumnHeaderCell>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          <Table.Row>
            <Table.Cell>
              <Entity icon={UserIcon} label="admin" to="" />
              {' '}
            </Table.Cell>
            <Table.Cell>10.x.x.x</Table.Cell>
            <Table.Cell className="flex flex-row gap-1" />
          </Table.Row>
        </Table.Body>
      </Table.Root>
    </AdminSidebar>
  );
}
