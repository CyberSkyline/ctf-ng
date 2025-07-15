import {
  Button,
  Container,
  Heading,
  Select,
  Table,
  TextArea,
  Text,
  Flex,
  Box,
} from '@radix-ui/themes';
import { TbSend } from 'react-icons/tb';

/**
 * Page for admins to send notifications to users.
 */
export default function AdminNotifications() {
  return (
    <Container size="4">
      <Flex direction="column" gap="4">
        <Box>
          <Heading>Send Notification</Heading>
          <Text>Recipient</Text>
          <br />
          <Select.Root defaultValue="all">
            <Select.Trigger className="!mb-2 !w-64" />
            <Select.Content>
              <Select.Item value="all">All Users</Select.Item>
              <Select.Item value="event-a">Event A</Select.Item>
              <Select.Item value="event-b">Event B</Select.Item>
              <Select.Item value="event-c">Event C</Select.Item>
            </Select.Content>
          </Select.Root>
          <br />
          <Text>Message</Text>
          <TextArea placeholder="Message to send..." className="h-64" mb="2" resize="vertical" />

          <Button variant="soft" className="mb-2">
            <TbSend />
            Send
          </Button>
        </Box>
        <Box>
          <Heading>Past Notifications</Heading>
          <Table.Root>
            <Table.Header>
              <Table.Row>
                <Table.ColumnHeaderCell>Message</Table.ColumnHeaderCell>
                <Table.ColumnHeaderCell>Recipients</Table.ColumnHeaderCell>
                <Table.ColumnHeaderCell>Date</Table.ColumnHeaderCell>
              </Table.Row>
            </Table.Header>
            <Table.Body>
              <Table.Row>
                <Table.Cell>Welcome to PC7!</Table.Cell>
                <Table.Cell>All Users</Table.Cell>
                <Table.Cell>yyyy-mm-dd 12:00</Table.Cell>
              </Table.Row>
            </Table.Body>
          </Table.Root>
        </Box>
      </Flex>
    </Container>
  );
}
