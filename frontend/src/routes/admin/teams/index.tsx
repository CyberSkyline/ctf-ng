import { Callout, Flex, Heading } from '@radix-ui/themes';
import { TbInfoCircle } from 'react-icons/tb';
import { AgGridReact } from 'ag-grid-react';
import type { ColDef } from 'ag-grid-community';
import { radixTheme } from '@/grid';

/**
 * Team management page for admins.
 */
export default function AdminTeams() {
  const rowData = [
    {
      name: 'Team 1234', event: 'pc7-teams', status: 'Started', members: '5/5', submissions: '10', score: '150', challenges: '3',
    },
    {
      name: 'Team 5678', event: 'pc7-teams', status: 'Not Started', members: '2/5', submissions: '0', score: '0', challenges: '0',
    },
    {
      name: 'user123', event: 'pc7-individual', status: 'Started', members: '1/1', submissions: '5', score: '75', challenges: '2',
    },
  ];
  const colDefs: ColDef<typeof rowData[number]>[] = [
    { field: 'name' },
    { field: 'event' },
    { field: 'status', width: 150 },
    { field: 'members', width: 100 },
    { field: 'submissions' },
    { field: 'score', width: 100 },
    { field: 'challenges', headerName: 'Active Challenges' },
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
        <Heading>Members</Heading>
        <Callout.Root variant="surface" color="jade">
          <Callout.Icon>
            <TbInfoCircle />
          </Callout.Icon>
          <Callout.Text>
            List of team members linking to user entries. Also controls to add/drop team members.
          </Callout.Text>
        </Callout.Root>

        <Heading>Submissions</Heading>
        <Callout.Root variant="surface" color="jade">
          <Callout.Icon>
            <TbInfoCircle />
          </Callout.Icon>
          <Callout.Text>
            Recent flag submissions made by the team.
          </Callout.Text>
        </Callout.Root>

        <Heading>
          Challenges
        </Heading>
        <Callout.Root variant="surface" color="jade">
          <Callout.Icon>
            <TbInfoCircle />
          </Callout.Icon>
          <Callout.Text>
            Challenge instances provisioned for this team.
          </Callout.Text>
        </Callout.Root>
      </Flex>
    </Flex>
  );
}
