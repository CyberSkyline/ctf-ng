import { EventIcon } from '@/constants';
import type { Team } from '@/types';
import type { ColDef, ICellRendererParams } from 'ag-grid-community';
import AdminGrid from 'components/AdminGrid';
import Entity from 'components/Entity';
import MemberCountBadge from 'components/MemberCountBadge';
import TeamSidebar from './TeamSidebar';

// cellDataType is pinned explicitly. The infinite row model has no rowData for ag-grid to infer types from.
const colDefs: ColDef<Team>[] = [
  {
    field : 'id',
    width : 100,
    headerName : 'ID',
    cellDataType : 'number',
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'name',
    width : 250,
    cellDataType : 'text',
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'event_name',
    headerName : 'Event',
    width : 250,
    cellDataType : 'text',
    filter : true,
    floatingFilter : true,
    cellRenderer : (params: ICellRendererParams<Team>) => params.data && (
      <Entity
        icon={EventIcon}
        label={params.data.event_name ?? `UNKNOWN (${params.data.event_id})`}
        to={`/admin/events?id=${params.data.event_id}`}
      />
    ),
  },
  {
    field : 'member_count',
    headerName : 'Members',
    width : 100,
    cellDataType : 'number',
    cellRenderer : (params: ICellRendererParams<Team>) => params.data && MemberCountBadge({ team : params.data }),
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
  },
  {
    field : 'end_time',
    headerName : 'End Time',
    width : 200,
    cellDataType : 'dateString',
    filter : 'agDateColumnFilter',
    floatingFilter : true,
  },
  {
    field : 'ranked',
    width : 100,
    cellDataType : 'boolean',
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'invite_code',
    headerName : 'Invite Code',
    width : 320,
    cellDataType : 'text',
    filter : true,
    floatingFilter : true,
  },
];

/**
 * Team management page for admins.
 */
export default function AdminTeams() {
  return (
    <>
      <title>Admin Teams</title>
      <AdminGrid
        collectionKey="/admin/teams"
        columnDefs={colDefs}
        getRowId={(params) => params.data.id.toString()}
        sidebarComponent={TeamSidebar}
        stopCellSelection={[ 'event_name' ]}
      />
    </>
  );
}
