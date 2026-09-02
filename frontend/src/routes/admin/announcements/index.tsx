import { Flex } from '@radix-ui/themes';
import { useAnnouncements } from '@/hooks/announcements';
import AdminGrid from 'components/AdminGrid';
import { ErrorCallout } from 'components/Callouts';
import Entity from 'components/Entity';
import AnnouncementTypeBadge from 'components/AnnouncementTypeBadge';
import { UserIcon } from '@/constants';
import type { ColDef, ICellRendererParams } from 'ag-grid-community';
import type { Announcement } from '@/types';
import AnnouncementModal from './AnnouncementModal';
import AnnouncementSidebar from './AnnouncementSidebar';

const colDefs: ColDef<Announcement>[] = [
  {
    field : 'id',
    headerName : 'ID',
  }, {
    field : 'title',
    headerName : 'Title',
    filter : true,
  }, {
    field : 'message',
    headerName : 'Message',
  }, {
    field : 'sender_name',
    headerName : 'Sender',
    filter : true,
    cellRenderer : Entity,
    cellRendererParams : (params: ICellRendererParams<Announcement>) => ({
      icon : UserIcon,
      label : params.data?.sender_name ?? `UNKNOWN (${params.data?.sender_id})`,
      to : `/admin/users?id=${params.data?.sender_id}`,
    }),
  }, {
    field : 'created_at',
    headerName : 'Created Date',
    cellDataType : 'dateString',
  }, {
    field : 'expires_at',
    headerName : 'Expiration Date',
    cellDataType : 'dateString',
  }, {
    field : 'type',
    headerName : 'Type',
    cellRenderer : (params: ICellRendererParams<Announcement>) => <AnnouncementTypeBadge type={params.value} />,
  },
];

export default function AdminAnnouncements() {
  const { data, error, isLoading } = useAnnouncements();

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  return (
    <>
      <title>Admin Announcements</title>
      <AdminGrid
        rowData={data ?? []}
        columnDefs={colDefs}
        loading={isLoading}
        getRowId={(params) => params.data.id.toString()}
        sidebarComponent={AnnouncementSidebar}
        toolbar={(
          <Flex direction="row" justify="start">
            <AnnouncementModal />
          </Flex>
        )}
      />
    </>
  );
}
