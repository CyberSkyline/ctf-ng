import { Box, Flex, Heading } from '@radix-ui/themes';
import { useAnnouncements } from '@/hooks/announcements';
import { ErrorCallout } from 'components/Callouts';
import Entity from 'components/Entity';
import { UserIcon } from '@/constants';
import type { ColDef } from 'ag-grid-community';
import type { Announcement } from '@/types';
import { AgGridReact } from 'ag-grid-react';
import { radixTheme } from '@/grid';
import CreateAnnoucementModal from './CreateAnnouncementModal';

const colDefs: ColDef<Announcement>[] = [
  {
    field : 'id',
    headerName : 'ID',
  }, {
    field : 'title',
    headerName : 'Title',
  }, {
    field : 'message',
    headerName : 'Message',
  }, {
    field : 'sender_name',
    headerName : 'Sender',
    cellRenderer : Entity,
    cellRendererParams : (params: {data: {sender_id?: number, sender_name?: string}}) => ({
      icon : UserIcon,
      label : params.data.sender_name ?? `UNKNOWN (${params.data.sender_id})`,
      to : `/admin/users?id=${params.data.sender_id}`,
    }),
  }, {
    field : 'created_at',
    headerName : 'Created Date',
    valueFormatter : (params) => params.value?.toLocaleString(),
  }, {
    field : 'expires_at',
    headerName : 'Expiration Date',
    valueFormatter : (params) => params.value?.toLocaleString(),
  }, {
    field : 'type',
    headerName : 'type',
  },
];

export default function AdminAnnouncements() {
  const { data, error, isLoading } = useAnnouncements();
  const rowData = data ?? [];

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  return (
    <Flex gap="3" direction="column">
      <Heading size="7">Announcements</Heading>
      <Box maxWidth="200px">
        <CreateAnnoucementModal />
      </Box>
      <AgGridReact
        theme={radixTheme}
        rowData={rowData}
        columnDefs={colDefs}
        domLayout="autoHeight"
        loading={isLoading}
      />
    </Flex>
  );
}
