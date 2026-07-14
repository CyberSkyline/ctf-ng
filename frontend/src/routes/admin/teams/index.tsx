import { EventIcon } from '@/constants';
import { useAllTeams } from '@/hooks/team';
import type { Team } from '@/types';
import { formatDate } from '@/util';
import type { ColDef } from 'ag-grid-community';
import AdminGrid from 'components/AdminGrid';
import { ErrorCallout } from 'components/Callouts';
import Entity from 'components/Entity';
import MemberCountBadge from 'components/MemberCountBadge';
import TeamSidebar from './TeamSidebar';

const colDefs: ColDef<Team>[] = [
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
    field : 'event_name',
    headerName : 'Event',
    width : 250,
    filter : true,
    floatingFilter : true,
    cellRenderer : Entity,
    cellRendererParams : (params: { data: {event_name?: string, event_id: number} }) => ({
      icon : EventIcon,
      label : params.data.event_name ?? `UNKNOWN (${params.data.event_id})`,
      to : `/admin/events?id=${params.data.event_id}`,
    }),
  },
  {
    field : 'member_count',
    headerName : 'Members',
    width : 100,
    cellRenderer : (params: { data: Team }) => MemberCountBadge({ team : params.data }),
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'start_timestamp',
    headerName : 'Start Time',
    width : 200,
    cellDataType : 'dateString',
    filter : 'agDateColumnFilter',
    floatingFilter : true,
    valueFormatter : ({ value }) => formatDate(value),
  },
  {
    field : 'end_time',
    headerName : 'End Time',
    width : 200,
    cellDataType : 'dateString',
    filter : 'agDateColumnFilter',
    floatingFilter : true,
    valueFormatter : ({ value }) => formatDate(value),
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
    width : 320,
    filter : true,
    floatingFilter : true,
  },
];

/**
 * Team management page for admins.
 */
export default function AdminTeams() {
  const { data, error, isLoading } = useAllTeams();

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  const rowData = data ?? [];

  return (
    <>
      <title>Admin Teams</title>
      <AdminGrid
        rowData={rowData}
        columnDefs={colDefs}
        loading={isLoading}
        getRowId={(params) => params.data.id.toString()}
        sidebarComponent={TeamSidebar}
        stopCellSelection={[ 'event_name' ]}
      />
    </>
  );
}
