import { Callout, Flex, Heading } from '@radix-ui/themes';
import type { ColDef } from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import { TbInfoCircle } from 'react-icons/tb';
import { radixTheme } from '@/grid';

/**
 * Event management page for admins, will also include challenge YAML uploading.
 */
export default function AdminEvents() {
  const rowData = [
    {
      name: 'PC7 Teams Round 1', start: 'date', end: 'date', teamSize: '5', registeredTeams: '10', registeredUsers: '50',
    },
  ];

  const colDefs: ColDef<typeof rowData[number]>[] = [
    { field: 'name' },
    { field: 'start' },
    { field: 'end' },
    { field: 'teamSize', headerName: 'Max Team Size' },
    { field: 'registeredTeams' },
    { field: 'registeredUsers' },
  ];

  return (
    <Flex direction="row" gap="4" className="h-full w-full">
      <AgGridReact
        className="grow basis-2/3"
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
      <Flex direction="column" gap="4" className="grow basis-1/3">
        <Heading>Information</Heading>
        <Callout.Root variant="surface" color="jade">
          <Callout.Icon>
            <TbInfoCircle />
          </Callout.Icon>
          <Callout.Text>
            Event info form. Configure name, description, start/end, team size, time limit, etc.
          </Callout.Text>
        </Callout.Root>

        <Heading>Challenges</Heading>
        <Callout.Root variant="surface" color="jade">
          <Callout.Icon>
            <TbInfoCircle />
          </Callout.Icon>
          <Callout.Text>
            Table of challenges associated with the event, with yaml dropzone/upload.
          </Callout.Text>
        </Callout.Root>
      </Flex>
    </Flex>
  );
}
