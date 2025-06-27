import {
  Button, Flex,
} from '@radix-ui/themes';
import type { ColDef } from 'ag-grid-community';
import { TbPlus } from 'react-icons/tb';
import { apiMutation } from '@/fetchers';
import { useEvents } from '@/hooks/events';
import { useSearchParams } from 'react-router';
import AdminGrid from 'components/AdminGrid';
import { ErrorCallout } from 'components/Callouts';
import EventSidebar from './EventSidebar';

/**
 * Event management page for admins, will also include challenge YAML uploading.
 */
export default function AdminEvents() {
  const { data, error, isLoading } = useEvents();
  const [ searchParams ] = useSearchParams();

  const eventId = searchParams.get('id');

  const rowData = data?.events ?? [];

  const colDefs: ColDef<typeof rowData[number]>[] = [
    { field : 'id', width : 100, headerName : 'ID' },
    { field : 'name', width : 250 },
    { field : 'description', flex : 1 },
    {
      field : 'start_time', headerName : 'Start Time', sort : 'desc', valueFormatter : (params) => params.value && new Date(params.value).toLocaleString(),
    },
    {
      field : 'end_time', headerName : 'End Time', valueFormatter : (params) => params.value && new Date(params.value).toLocaleString(),
    },
    {
      field : 'locked', width : 100,
    },
  ];

  if (error) {
    return (<ErrorCallout>{error.message}</ErrorCallout>);
  }

  return (
    <Flex direction="column" gap="4" className="h-full w-full">
      <Flex direction="row" gap="4" className="shrink-0">
        <Button onClick={() => {
          apiMutation('/events', {
            name : 'New Event',
            description : 'Event description',
            start_time : '2025-07-04T12:00:00',
            end_time : '2025-07-04T14:00:00',
            max_team_size : 5,
            locked : false,
          }, {
            method : 'POST',
          });
        }}
        >
          <TbPlus />
          Create Event
        </Button>
      </Flex>
      <Flex direction="row" gap="4" className="grow">
        <AdminGrid
          rowData={rowData}
          columnDefs={colDefs}
          loading={isLoading}
          getRowId={(params) => params.data.id.toString()}
        />
        <Flex direction="column" gap="4" className="w-128 grow-0 shrink-0 overflow-y-auto">
          <EventSidebar key={eventId} />
        </Flex>
      </Flex>
    </Flex>
  );
}
