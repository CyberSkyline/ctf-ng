import { useAllEvents } from '@/hooks/events';
import type { AdminEvent } from '@/types';
import { Flex } from '@radix-ui/themes';
import type { ColDef } from 'ag-grid-community';
import AdminGrid from 'components/AdminGrid';
import { ErrorCallout } from 'components/Callouts';
import EventCreationModal from './EventCreationModal';
import EventSidebar from './SidebarTabs';

const colDefs: ColDef<AdminEvent>[] = [
  {
    field : 'id',
    width : 100,
    headerName : 'ID',
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'name',
    width : 250,
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'description',
    width : 300,
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'start_time',
    headerName : 'Start Time',
    sort : 'desc',
    cellDataType : 'dateString',
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'end_time',
    headerName : 'End Time',
    cellDataType : 'dateString',
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'registration_start_date',
    headerName : 'Registration Start',
    cellDataType : 'dateString',
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'registration_end_date',
    headerName : 'Registration End',
    cellDataType : 'dateString',
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'max_team_size',
    width : 150,
    headerName : 'Max Team Size',
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'public',
    width : 100,
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'registration_open',
    width : 100,
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'locked',
    width : 100,
    filter : true,
    floatingFilter : true,
  },
];

/**
 * Event management page for admins, will also include challenge YAML uploading.
 */
export default function AdminEvents() {
  const { data, error, isLoading } = useAllEvents();
  const rowData = data ?? [];

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  return (
    <>
      <title>Admin Events</title>
      <AdminGrid
        rowData={rowData}
        columnDefs={colDefs}
        loading={isLoading}
        getRowId={(params) => params.data.id.toString()}
        sidebarComponent={EventSidebar}
        toolbar={(
          <Flex direction="row" justify="start">
            <EventCreationModal />
          </Flex>
        )}
      />
    </>
  );
}
