import type { ColDef } from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import { useState } from 'react';
import {
  Button, Callout, Flex, Heading,
} from '@radix-ui/themes';
import {
  TbInfoCircle, TbPlus, TbTrash,
} from 'react-icons/tb';
import { radixTheme } from '../../../grid';

/**
 * User management page for admins.
 */
export default function AdminUsers() {
  const [rowData] = useState([
    {
      name: 'Alice', role: 'Admin', uuid: '550e8400-e29b-41d4-a716-446655440000', lastLogin: 'xxxx-yy-zz',
    },
    {
      name: 'Bob', role: 'User', uuid: '550e8400-e29b-41d4-a716-446655440001', lastLogin: 'xxxx-yy-zz',
    },
    {
      name: 'Charlie', role: 'Support', uuid: '550e8400-e29b-41d4-a716-446655440002', lastLogin: 'xxxx-yy-zz',
    },
    {
      name: 'David', role: 'User', uuid: '550e8400-e29b-41d4-a716-446655440003', lastLogin: 'xxxx-yy-zz',
    },
    {
      name: 'Eve', role: 'Admin', uuid: '550e8400-e29b-41d4-a716-446655440004', lastLogin: 'xxxx-yy-zz',
    },
  ]);

  const [colDefs] = useState<ColDef<typeof rowData[number]>[]>([
    { field: 'name' },
    { field: 'role' },
    { field: 'uuid' },
    { field: 'lastLogin', width: 150 },
  ]);

  return (
    <Flex direction="row" gap="4" className="w-full h-full">
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
      <Flex direction="column" gap="4" height="100%" flexGrow="1" className="basis-1/3" overflowY="auto">
        <Flex direction="row" gap="2" justify="between" align="center">
          <Heading>Information</Heading>
          <Button variant="soft" color="red">
            <TbTrash />
            Delete
          </Button>
        </Flex>
        <Callout.Root
          color="jade"
          variant="surface"
        >
          <Callout.Icon>
            <TbInfoCircle />
          </Callout.Icon>
          <Callout.Text>
            User info form with name, role, etc.
          </Callout.Text>
        </Callout.Root>
        <Heading>Workspace</Heading>
        <Callout.Root
          color="jade"
          variant="surface"
        >
          <Callout.Icon>
            <TbInfoCircle />
          </Callout.Icon>
          <Callout.Text>
            Information about the user&apos;s workspace and relevant admin actions.
            (Remote access, restart, etc.)
          </Callout.Text>
        </Callout.Root>

        <Flex direction="row" gap="2" justify="between" align="center">
          <Heading>Registrations</Heading>
          <Button variant="soft">
            <TbPlus />
            Register
          </Button>
        </Flex>
        <Callout.Root
          color="jade"
          variant="surface"
        >
          <Callout.Icon>
            <TbInfoCircle />
          </Callout.Icon>
          <Callout.Text>
            Table of events the user is registered for,
            linking to each team and event.
          </Callout.Text>
        </Callout.Root>
      </Flex>

    </Flex>
  );
}
