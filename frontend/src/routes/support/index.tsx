import {
  Badge, Box, Button, Container, Flex, Heading,
} from '@radix-ui/themes';
import { AgGridReact } from 'ag-grid-react';
import type { ColDef, ICellRendererParams } from 'ag-grid-community';
import { useNavigate } from 'react-router';
import { radixTheme } from '@/grid';

function StatusBadge({ value }: ICellRendererParams) {
  switch (value) {
    case 'closed': return <Badge color="jade">Closed</Badge>;
    case 'inprogress': return <Badge color="blue">In Progress</Badge>;
    default: return <Badge color="orange">Open</Badge>;
  }
}

export default function Support() {
  const navigate = useNavigate();
  const rowData = [
    {
      id: '1', subject: 'test ticket 1', event: 'track 1 round 1', status: 'open', created: '2022-02-14', updated: '2022-02-15',
    },
    {
      id: '3', subject: 'test ticket 3', event: 'track 1 round 3', status: 'inprogress', created: '2022-02-14', updated: '2022-02-15',
    },
    {
      id: '2', subject: 'test ticket 2', event: 'track 1 round 2', status: 'closed', created: '2022-02-14', updated: '2022-02-15',
    },
  ];

  const colDefs: ColDef<typeof rowData[number]>[] = [
    { field: 'subject' },
    { field: 'event' },
    { field: 'status', cellRenderer: StatusBadge },
    { field: 'created', valueFormatter: (params) => new Date(params.value).toString() },
    { field: 'updated', valueFormatter: (params) => new Date(params.value).toString() },
  ];

  return (
    <Container size="4">
      <Flex gap="3" direction="column">
        <Heading size="7">Support Tickets</Heading>
        <Box maxWidth="200px">
          <Button
            onClick={() => navigate('/support/createTicket')}
          >
            Create Ticket
          </Button>
        </Box>
        <AgGridReact
          theme={radixTheme}
          rowData={rowData}
          columnDefs={colDefs}
          domLayout="autoHeight"
          onRowClicked={(e) => navigate(`/support/${e.data?.id}`)}
        />
      </Flex>
    </Container>
  );
}
