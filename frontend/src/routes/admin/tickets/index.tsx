import {
  Button, Card, Flex, Heading, Text, TextArea,
} from '@radix-ui/themes';
import type { ColDef } from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import { radixTheme } from '../../../grid';

/**
 * Support ticket management page for admins.
 */
export default function AdminTickets() {
  const rowData = [
    {
      subject: 'Help!!!', user: 'user123', status: 'Open', created: 'xxxx-yy-zz', updated: 'aaaa-bb-cc', event: 'pc7-teams', challenge: null,
    },
  ];
  const colDefs: ColDef<typeof rowData[number]>[] = [
    { field: 'subject' },
    { field: 'user' },
    { field: 'status', width: 100 },
    { field: 'created', width: 150 },
    { field: 'updated', width: 150 },
    { field: 'event' },
    { field: 'challenge' },
  ];

  return (
    <Flex direction="row" gap="4" className="h-full w-full">
      <AgGridReact
        className="grow basis-1/2"
        theme={radixTheme}
        rowData={rowData}
        columnDefs={colDefs}
        gridOptions={{
          rowSelection: {
            mode: 'singleRow',
            checkboxes: false,
            enableClickSelection: true,
          },
        }}
      />
      <Flex direction="column" gap="4" className="grow basis-1/2">
        <Flex direction="column" gap="4" flexGrow="1" overflowY="auto">
          <Card className="shrink-0">
            <Heading>Message</Heading>
            <Text as="p">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit.
              Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
              Alienum in tempor orci dapibus ultrices in iaculis nunc sed augue.
            </Text>
          </Card>
          <Card className="shrink-0">
            <Heading>Message</Heading>
            <Text as="p">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit.
              Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
              Alienum in tempor orci dapibus ultrices in iaculis nunc sed augue.
            </Text>
          </Card>
          <Card className="shrink-0">
            <Heading>Message</Heading>
            <Text as="p">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit.
              Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
              Alienum in tempor orci dapibus ultrices in iaculis nunc sed augue.
            </Text>
          </Card>
        </Flex>
        <TextArea placeholder="Response" />
        <Button variant="soft">
          Send
        </Button>
      </Flex>
    </Flex>
  );
}
