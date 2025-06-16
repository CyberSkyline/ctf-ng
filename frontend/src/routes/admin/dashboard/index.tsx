import {
  Callout, Card, Flex, Heading, Table, Text,
} from '@radix-ui/themes';
import AdminEventCard from 'components/admin/AdminEventCard';
import Statistic from 'components/admin/Statistic';
import {
  TbAlertTriangle,
} from 'react-icons/tb';

/**
 * Admin dashboard with system monitoring and important metrics.
 */
export default function AdminDashboard() {
  return (
    <>
      <Callout.Root
        color="amber"
        variant="surface"
        mb="4"
      >
        <Callout.Icon>
          <TbAlertTriangle />
        </Callout.Icon>
        <Callout.Text>
          Something bad happened!
        </Callout.Text>
      </Callout.Root>

      <Flex direction={{ initial: 'column', lg: 'row' }} gap="4">
        <Flex direction="column" gap="4" className="flex-grow basis-1/2 h-full">
          <Card>
            <Flex gap="4">
              <Statistic label="Active Users" value={123} delta="+10%" description="Number of active user sessions." />
              <Statistic label="Something" value={456} delta="-10%" description="Number of something." />
              <Statistic label="Errors" value={0} />
            </Flex>
          </Card>
          <Card className="h-128">
            Graph of activity
          </Card>
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
                <Table.Row>
                  <Table.Cell>instance-1</Table.Cell>
                  <Table.Cell>Healthy</Table.Cell>
                  <Table.Cell>193</Table.Cell>
                  <Table.Cell>1h 23m</Table.Cell>
                  <Table.Cell>10%</Table.Cell>
                  <Table.Cell>512MB</Table.Cell>
                  <Table.Cell>1GB</Table.Cell>
                </Table.Row>
                <Table.Row>
                  <Table.Cell>instance-2</Table.Cell>
                  <Table.Cell>Healthy</Table.Cell>
                  <Table.Cell>191</Table.Cell>
                  <Table.Cell>1h 23m</Table.Cell>
                  <Table.Cell>20%</Table.Cell>
                  <Table.Cell>512MB</Table.Cell>
                  <Table.Cell>1GB</Table.Cell>
                </Table.Row>
                <Table.Row>
                  <Table.Cell>instance-3</Table.Cell>
                  <Table.Cell>Healthy</Table.Cell>
                  <Table.Cell>195</Table.Cell>
                  <Table.Cell>1h 23m</Table.Cell>
                  <Table.Cell><Text color="red">90%</Text></Table.Cell>
                  <Table.Cell>512MB</Table.Cell>
                  <Table.Cell>1GB</Table.Cell>
                </Table.Row>
              </Table.Body>
            </Table.Root>
          </Card>
        </Flex>
        <Flex direction="column" gap="4" flexGrow="1" flexBasis="50%">
          <AdminEventCard id="event1" />
          <AdminEventCard id="event2" />
          <AdminEventCard id="event3" />
        </Flex>
      </Flex>

    </>
  );
}
