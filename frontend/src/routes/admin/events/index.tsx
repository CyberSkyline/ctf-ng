import { Button, Dialog, Flex } from '@radix-ui/themes';
import type { ColDef } from 'ag-grid-community';
import { TbPlus } from 'react-icons/tb';
import { createEvent, useAllEvents } from '@/hooks/events';
import AdminGrid from 'components/AdminGrid';
import { ErrorCallout } from 'components/Callouts';
import { useState } from 'react';
import EventSidebar from './EventSidebar';
import EventDataForm from './EventDataForm';

/**
 * Event management page for admins, will also include challenge YAML uploading.
 */
export default function AdminEvents() {
  const { data, error, isLoading } = useAllEvents();
  const rowData = data ?? [];

  const colDefs: ColDef<typeof rowData[number]>[] = [
    {
      field : 'name', width : 250, filter : true, floatingFilter : true,
    },
    {
      field : 'description', width : 300, filter : true, floatingFilter : true,
    },
    {
      field : 'start_time',
      headerName : 'Start Time',
      sort : 'desc',
      valueFormatter : (params) => params.value && params.value.toLocaleString(),
      filter : true,
      floatingFilter : true,
    },
    {
      field : 'end_time',
      headerName : 'End Time',
      valueFormatter : (params) => params.value && params.value.toLocaleString(),
      filter : true,
      floatingFilter : true,
    },
    {
      field : 'registration_start_date',
      headerName : 'Registration Start',
      valueFormatter : (params) => params.value && params.value.toLocaleString(),
      filter : true,
      floatingFilter : true,
    },
    {
      field : 'registration_end_date',
      headerName : 'Registration End',
      valueFormatter : (params) => params.value && params.value.toLocaleString(),
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
    {
      field : 'id',
      width : 100,
      headerName : 'ID',
      filter : true,
      floatingFilter : true,
    },
  ];

  const [ open, setOpen ] = useState(false);

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  return (
    <Flex direction="column" gap="4" className="h-full w-full">
      <Flex direction="row" gap="4" className="shrink-0">
        <Dialog.Root open={open} onOpenChange={setOpen}>
          <Dialog.Trigger>
            <Button variant="solid">
              <TbPlus />
              Create Event
            </Button>
          </Dialog.Trigger>
          <Dialog.Content>
            <Dialog.Title>Create New Event</Dialog.Title>
            <EventDataForm onSubmit={(d) => {
              createEvent(d);

              // close the dialog after submission
              setOpen(false);
            }}
            />
          </Dialog.Content>
        </Dialog.Root>
      </Flex>
      <Flex direction="row" gap="4" className="grow">
        <AdminGrid
          rowData={rowData}
          columnDefs={colDefs}
          loading={isLoading}
          getRowId={(params) => params.data.id.toString()}
          sidebarComponent={EventSidebar}
        />
      </Flex>
    </Flex>
  );
}
