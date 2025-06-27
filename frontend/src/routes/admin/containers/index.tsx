import { Flex, Heading } from '@radix-ui/themes';
import { AgGridReact } from 'ag-grid-react';
import type { ColDef } from 'ag-grid-community';
import { radixTheme } from '@/grid';
import { InfoCallout } from 'components/Callouts';

/**
 * Admin page to manage challenge networks/containers.
 * The datagrid will list full challenge deployments/networks with aggregate stats,
 * and selecting one will show the individual containers within the deployment.
 */
export default function AdminContainers() {
  const rowData = [
    {
      challenge : 'challengename1', event : 'pc7-teams', team : 'teamname', containers : '2/2', workspaces : '1', cpu : '10%', memory : '512MiB',
    },
  ];
  const colDefs: ColDef<typeof rowData[number]>[] = [
    { field : 'challenge' },
    { field : 'event' },
    { field : 'team' },
    {
      field : 'containers',
      width : 120,
    },
    {
      field : 'workspaces',
      headerName : 'Attached Workspaces',
    },
    { field : 'cpu' },
    { field : 'memory' },
  ];

  return (
    <Flex direction="row" gap="4" className="h-full w-full">
      <AgGridReact
        className="grow basis-2/3"
        theme={radixTheme}
        rowData={rowData}
        columnDefs={colDefs}
        gridOptions={{
          rowSelection : {
            mode : 'singleRow',
            checkboxes : false,
            enableClickSelection : true,
          },
        }}
      />
      <Flex direction="column" gap="4" className="grow basis-1/3">
        <Heading>Services</Heading>
        <InfoCallout>List of containers that are part of the challenge with statuses, resource usage, and actions.</InfoCallout>

        <Heading>Network</Heading>
        <InfoCallout>Information about the challenge container network, like address space.</InfoCallout>

        <Heading>
          Variables
        </Heading>
        <InfoCallout>Faker-generated challenge variables for this challenge instance.</InfoCallout>

        <Heading>Workspaces</Heading>
        <InfoCallout>Links to user workspaces attached to this container network, if any.</InfoCallout>
      </Flex>
    </Flex>
  );
}
