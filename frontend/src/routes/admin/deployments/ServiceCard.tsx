import { COLOR_NEGATIVE, COLOR_POSITIVE } from '@/constants';
import { useContainerStatus } from '@/hooks/container';
import type { ContainerInstance } from '@/types';
import {
  Badge,
  Box,
  Card,
  Code,
  Flex,
  Heading,
  Skeleton,
  Text,
  Tooltip,
} from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import { upperCase } from 'lodash';
import ContainerExecModal from './ContainerExecModal';
import ContainerLogsModal from './ContainerLogsModal';
import RecycleContainerModal from './RecycleContainerModal';
import RestartContainerModal from './RestartContainerModal';

export default function ServiceCard({ service }: { service: ContainerInstance }) {
  const { data : statusData, error } = useContainerStatus(service.id);

  const { dockerid, hostip } = service;
  const {
    name, image, status, env,
  } = statusData || {};

  return (
    <Card key={service.id}>
      {error && <ErrorCallout>{error.message}</ErrorCallout>}
      <Flex direction="column" gap="2">
        <Flex direction="row" align="start" justify="between" gap="2">
          <Box>
            <Skeleton loading={!statusData}><Heading size="4">{name || 'Unknown'}</Heading></Skeleton>
            <Skeleton loading={!statusData}><Text color="gray">{image || 'unknown'}</Text></Skeleton>
          </Box>
          <Box className="text-right">
            <Skeleton loading={!statusData}>
              <Badge color={status === 'running' ? COLOR_POSITIVE : COLOR_NEGATIVE}>
                {upperCase(status || 'unknown')}
              </Badge>
            </Skeleton>
            <br />
            <Tooltip content={<Text>{dockerid}</Text>}>
              <Text color="gray">{dockerid.slice(0, 12)}</Text>
            </Tooltip>
            <br />
            <Text color="gray">{hostip}</Text>
          </Box>
        </Flex>
        <Skeleton loading={!statusData}>
          <details>
            <summary>Environment</summary>
            <Code color="gray" className="block whitespace-pre overflow-auto max-h-32">
              {env?.join('\n')}
            </Code>
          </details>
        </Skeleton>
        <Flex direction="row" gap="4">
          <RecycleContainerModal containerId={service.id} />
          <RestartContainerModal containerId={service.id} />
          <ContainerLogsModal containerId={service.id} />
          <ContainerExecModal containerId={service.id} />
        </Flex>
      </Flex>
    </Card>
  );
}
