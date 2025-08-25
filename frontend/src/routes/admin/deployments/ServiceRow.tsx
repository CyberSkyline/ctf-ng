import { COLOR_NEGATIVE, COLOR_POSITIVE } from '@/constants';
import { useContainerStatus } from '@/hooks/container';
import type { ContainerInstance } from '@/types';
import {
  Badge,
  Code,
  Skeleton,
  Table,
  Text,
  Tooltip,
} from '@radix-ui/themes';
import { upperCase } from 'lodash';
import ContainerLogsModal from './ContainerLogsModal';
import RecycleContainerModal from './RecycleContainerModal';
import RestartContainerModal from './RestartContainerModal';

export default function ServiceRow({ service }: {service: ContainerInstance}) {
  const { data : status, error, isLoading } = useContainerStatus(service.id);
  return (
    <Table.Row key={service.id}>
      <Table.Cell>
        <Skeleton loading={isLoading}>
          {status?.name || error?.message || 'Loading...'}
        </Skeleton>
      </Table.Cell>
      <Table.Cell>
        <Skeleton loading={!status}>
          <Badge color={status?.status === 'running' ? COLOR_POSITIVE : COLOR_NEGATIVE}>
            {upperCase(status?.status || 'unknown')}
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
          {status?.image || 'unknown'}
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
