import {
  Callout, Flex, Heading,
} from '@radix-ui/themes';
import {
  TbInfoCircle,
} from 'react-icons/tb';
import { AgGridReact } from 'ag-grid-react';
import type { ColDef } from 'ag-grid-community';
import { radixTheme } from '../../../grid';

/**
 * Admin page to manage challenge networks/containers.
 * The datagrid will list full challenge deployments/networks with aggregate stats,
 * and selecting one will show the individual containers within the deployment.
 */
export default function AdminContainers() {
  const rowData = [
    {
      challenge: 'challengename1', event: 'pc7-teams', team: 'teamname', containers: '2/2', workspaces: '1', cpu: '10%', memory: '512MiB',
    },
  ];
  const colDefs: ColDef<typeof rowData[number]>[] = [
    { field: 'challenge' },
    { field: 'event' },
    { field: 'team' },
    {
      field: 'containers',
      width: 120,
    },
    {
      field: 'workspaces',
      headerName: 'Attached Workspaces',
    },
    { field: 'cpu' },
    { field: 'memory' },
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
        <Heading>Services</Heading>
        <Callout.Root variant="surface" color="jade">
          <Callout.Icon>
            <TbInfoCircle />
          </Callout.Icon>
          <Callout.Text>
            List of containers that are part of the challenge
            with statuses, resource usage, and actions.
          </Callout.Text>
        </Callout.Root>

        <Heading>Network</Heading>
        <Callout.Root variant="surface" color="jade">
          <Callout.Icon>
            <TbInfoCircle />
          </Callout.Icon>
          <Callout.Text>
            Information about the challenge container network, like address space.
          </Callout.Text>
        </Callout.Root>

        <Heading>
          Variables
        </Heading>
        <Callout.Root variant="surface" color="jade">
          <Callout.Icon>
            <TbInfoCircle />
          </Callout.Icon>
          <Callout.Text>
            Faker-generated challenge variables for this challenge instance.
          </Callout.Text>
        </Callout.Root>

        <Heading>Workspaces</Heading>
        <Callout.Root variant="surface" color="jade">
          <Callout.Icon>
            <TbInfoCircle />
          </Callout.Icon>
          <Callout.Text>
            Links to user workspaces attached to this container network, if any.
          </Callout.Text>
        </Callout.Root>
      </Flex>
    </Flex>
  );
}
