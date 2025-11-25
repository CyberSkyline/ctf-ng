import {
  Box,
  Button,
  Container,
  Flex,
  Heading,
} from '@radix-ui/themes';
import { AgGridReact } from 'ag-grid-react';
import type { ColDef } from 'ag-grid-community';
import { useNavigate } from 'react-router';
import { StatusBadgeCell } from 'components/StatusBadge';
import { radixTheme } from '@/grid';
import { useMyTickets } from '@/hooks/support';
import type { Ticket } from '@/types';
import { isUndefined } from 'lodash';
import { ErrorCallout } from 'components/Callouts';

export default function Support() {
  const navigate = useNavigate();

  const { data, error } = useMyTickets();

  const colDefs: ColDef<Ticket>[] = [
    { field : 'subject', headerName : 'Subject' },
    { field : 'event_name', headerName : 'Event Name' },
    { field : 'status', headerName : 'Status', cellRenderer : StatusBadgeCell },
    { field : 'opened_timestamp', headerName : 'Created Date', valueFormatter : (params) => params.value.toLocaleString() },
    { field : 'last_updated', headerName : 'Last Updated Date', valueFormatter : (params) => params.value.toLocaleString() },
  ];

  return (
    <Container size="4">
      <title>Support Tickets</title>
      {!isUndefined(error)
        ? <ErrorCallout>{error?.message}</ErrorCallout>
        : (
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
              rowData={data}
              columnDefs={colDefs}
              domLayout="autoHeight"
              onRowClicked={(e) => navigate(`/support/${e.data?.id}`)}
              defaultColDef={{ flex : 1 }}
            />
          </Flex>
        )}
    </Container>
  );
}
