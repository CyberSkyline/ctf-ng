import Statistic from 'components/Statistic';
import {
  Card,
  Flex,
  Heading,
  Table,
} from '@radix-ui/themes';

export default function AdminProvisionerCard() {
  const data = [
    {
      instance : 'instance-1',
      status : 'Healthy',
      containers : 193,
      uptime : '1h 23m',
      cpu : '10%',
      memory : '512MB',
      disk : '1GB',
    },
    {
      instance : 'instance-2',
      status : 'Healthy',
      containers : 191,
      uptime : '1h 23m',
      cpu : '20%',
      memory : '512MB',
      disk : '1GB',
    },
    {
      instance : 'instance-3',
      status : 'Healthy',
      containers : 195,
      uptime : '1h 23m',
      cpu : '90%',
      memory : '512MB',
      disk : '1GB',
    },
  ];

  return (
    <Card>
      <Heading>Provisioner</Heading>
      <Flex gap="4" my="4">
        <Statistic label="Total Containers" value={579} description="Number of containers across all instances." />
        <Statistic label="Challenge Containers" value={456} description="Number of running challenge containers." />
        <Statistic label="Workspace Containers" value={123} description="Number of running workspace containers." />
        <Statistic label="Container Networks" value={202} description="Number of active networks." />
      </Flex>
      <Table.Root>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeaderCell>Instance</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Status</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Containers</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Uptime</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>CPU</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Memory</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Disk</Table.ColumnHeaderCell>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {data.map((row) => (
            <Table.Row key={row.instance}>
              <Table.Cell>{row.instance}</Table.Cell>
              <Table.Cell>{row.status}</Table.Cell>
              <Table.Cell>{row.containers}</Table.Cell>
              <Table.Cell>{row.uptime}</Table.Cell>
              <Table.Cell>
                {row.cpu}
              </Table.Cell>
              <Table.Cell>{row.memory}</Table.Cell>
              <Table.Cell>{row.disk}</Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table.Root>
    </Card>
  );
}
