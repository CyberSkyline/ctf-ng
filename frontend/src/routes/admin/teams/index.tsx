import { useAllTeams } from '@/hooks/team';
import type { Team } from '@/types';
import type { ColDef } from 'ag-grid-community';
import AdminGrid from 'components/AdminGrid';
import { ErrorCallout } from 'components/Callouts';
import EventCellRenderer from 'components/EventCellRenderer';
import MemberCountBadge from 'components/MemberCountBadge';
import TeamSidebar from './TeamSidebar';

/**
 * Team management page for admins.
 */
export default function AdminTeams() {
  const { data, error, isLoading } = useAllTeams();

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  const rowData = data ?? [];

  const colDefs: ColDef<typeof rowData[number]>[] = [
    {
      field : 'name',
      width : 250,
      filter : true,
      floatingFilter : true,
    },
    {
      field : 'event_id',
      headerName : 'Event',
      width : 200,
      filter : 'agNumberColumnFilter',
      filterParams : {
        filterOptions : [ 'equals' ],
        maxNumConditions : 1,
      },
      floatingFilter : true,
      cellRenderer : EventCellRenderer,
    },
    {
      headerName : 'Members',
      width : 100,
      field : 'member_count',
      cellRenderer : (params: { data: Team }) => MemberCountBadge({ team : params.data }),
      filter : true,
      floatingFilter : true,
    },
    {
      field : 'ranked',
      width : 100,
      filter : true,
      floatingFilter : true,
    },
    {
      field : 'invite_code',
      headerName : 'Invite Code',
      width : 300,
      filter : true,
      floatingFilter : true,
    },
  ];

  return (
    <AdminGrid
      rowData={rowData}
      columnDefs={colDefs}
      loading={isLoading}
      getRowId={(params) => params.data.id.toString()}
      sidebarComponent={TeamSidebar}
    />
  );
}
