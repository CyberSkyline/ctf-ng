import {
  COLOR_INFO,
  COLOR_NEGATIVE,
  COLOR_POSITIVE,
  TeamIcon,
  UserIcon,
} from '@/constants';
import { useContainerStatus, useDeploymentServices } from '@/hooks/container';
import type { ContainerInstance, Deployment } from '@/types';
import {
  Badge,
  Button,
  Code,
  Skeleton,
  Table,
  Text,
  Tooltip,
} from '@radix-ui/themes';
import AdminDataList from 'components/AdminDataList';
import AdminSidebar from 'components/AdminSidebar';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import { ErrorCallout, WarningCallout } from 'components/Callouts';
import Entity from 'components/Entity';
import { upperCase } from 'lodash';
import { Link } from 'react-router';
import ContainerLogsModal from './ContainerLogsModal';
import RecycleContainerModal from './RecycleContainerModal';
import RestartContainerModal from './RestartContainerModal';

function ServiceRow({ service }: {service: ContainerInstance}) {
  const { data : status, error, isLoading } = useContainerStatus(service.id);
  return (
    <Table.Row key={service.id}>
      <Table.Cell>
        <Skeleton loading={isLoading}>
          {status?.name || error?.message || 'lorem-ipsum'}
        </Skeleton>
      </Table.Cell>
      <Table.Cell>
        <Skeleton loading={!status}>
          <Badge color={status?.status === 'running' ? COLOR_POSITIVE : COLOR_NEGATIVE}>
            {upperCase(status?.status) || 'lorem-ipsum'}
          </Badge>
        </Skeleton>
      </Table.Cell>

      <Table.Cell>
        <Tooltip content={<Text>{service?.dockerid}</Text>}>
          <Code color="gray">{service?.dockerid.slice(0, 12)}</Code>
        </Tooltip>
      </Table.Cell>
      <Table.Cell>
        <Skeleton loading={!status}>
          {status?.image || 'lorem-ipsum'}
        </Skeleton>
      </Table.Cell>
      <Table.Cell>
        {service?.hostip}
      </Table.Cell>
      <Table.Cell align="right">
        <ContainerLogsModal containerId={service.id} />
        <RestartContainerModal containerId={service.id} />
        <RecycleContainerModal containerId={service.id} />
      </Table.Cell>
    </Table.Row>
  );
}

export default function DeploymentSidebar({ entity }: {entity: Deployment}) {
  const { data : serviceData, error } = useDeploymentServices(entity.challenge_id, entity.team);

  return (
    <AdminSidebar>
      <AdminSidebarHeader title="Deployment Details">
        <Button variant="soft" color={COLOR_INFO} asChild>
          <Link to={`/admin/teams?id=${entity.team}`}>
            <TeamIcon />
            Team
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
