import { useSupportTags } from '@/hooks/support';
import type { TicketTag } from '@/types';
import type { ColDef, ICellRendererParams } from 'ag-grid-community';
import { ErrorCallout } from 'components/Callouts';
import { Box, Flex, Text } from '@radix-ui/themes';
import { radixTheme } from '@/grid';
import { AgGridReact } from 'ag-grid-react';
import TagModal from './TagModal';

function ColorFieldCell({ value }: ICellRendererParams) {
  return (
    <Flex gap="1" className="items-center mt-1">
      <Box
        width="16px"
        height="16px"
        style={{ backgroundColor : value }}
      />
      <Text className="pt-1">{value}</Text>
    </Flex>
  );
}

function ActionsCell({ data }: ICellRendererParams) {
  return (
    <div className="mt-1">
      <TagModal
        defaultValues={data}
      />
    </div>
  );
}

const colDefs: ColDef<TicketTag>[] = [
  {
    field : 'id',
  },
  {
    field : 'name',
  },
  {
    field : 'color',
    cellRenderer : ColorFieldCell,
  },
  {
    field : 'description',
  },
  {
    field : 'ticket_count',
    headerName : 'Ticket Count',
  },
  {
    headerName : 'Actions',
    cellRenderer : ActionsCell,
  },
];

export default function SupportTags() {
  const { data, error } = useSupportTags();

  return (
    <>
      {error && <ErrorCallout>{error.message}</ErrorCallout>}
      <div className="mb-2">
        <TagModal />
      </div>
      <AgGridReact
        theme={radixTheme}
        rowData={data || []}
        columnDefs={colDefs}
        domLayout="autoHeight"
      />
    </>
  );
}
