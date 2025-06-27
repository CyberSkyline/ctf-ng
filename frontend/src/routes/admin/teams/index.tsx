import {
  Flex,
} from '@radix-ui/themes';
import type { ColDef } from 'ag-grid-community';
import AdminGrid from 'components/AdminGrid';
import { useEventTeams } from '@/hooks/team';
import { ErrorCallout } from 'components/Callouts';
import TeamSidebar from './TeamSidebar';

/**
 * Team management page for admins.
 */
export default function AdminTeams() {
  // Since useTeams() is not available yet, hardcode the event ID for now.
  const { data, error, isLoading } = useEventTeams(2);

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  const rowData = data?.teams ?? [];

  const colDefs: ColDef<typeof rowData[number]>[] = [
    { field : 'name' },
    {
      // field : 'event_id',
      // Also hardcoded.
      valueGetter : () => 2,
      headerName : 'Event',
      width : 200,
      filter : 'agNumberColumnFilter',
      floatingFilter : true,
      // Will eventually be rendered as event name instead of ID.
      // Need to fetch in the cell renderer component.
    },
    {
      headerName : 'Members',
      width : 100,
      valueFormatter : (params) => `${params.data?.member_count}/${params.data?.max_team_size}`,
    },
    { field : 'ranked', width : 80 },
    {
      field : 'invite_code', headerName : 'Invite Code', width : 150,
    },
  ];

  return (
    <Flex direction="row" gap="4" className="h-full w-full">
      <AdminGrid
        rowData={rowData}
        columnDefs={colDefs}
        loading={isLoading}
        getRowId={(params) => params.data.id.toString()}
      />
      <Flex direction="column" gap="4" className="w-128 shrink-0 grow-0 overflow-y-auto">
        <TeamSidebar />
      </Flex>
    </Flex>
  );
}
