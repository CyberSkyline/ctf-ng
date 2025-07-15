import type { ColDef } from 'ag-grid-community';
import AdminGrid from 'components/AdminGrid';
import { ErrorCallout } from 'components/Callouts';
import type { Team } from '@/types';
import { useEvent } from '@/hooks/events';
import Entity from 'components/Entity';
import { useAllTeams } from '@/hooks/team';
import { useSearchParams } from 'react-router';
import { EventIcon } from '@/constants';
import MemberCountBadge from 'components/MemberCountBadge';
import TeamSidebar from './TeamSidebar';

function EventCellRenderer({ value }: { value: number }) {
  const { data, error, isLoading } = useEvent(value);

  if (isLoading) {
    return <span>Loading...</span>;
  }

  if (error) {
    return (
      <span>
        Error:
        {error.message}
      </span>
    );
  }

  return (
    <Entity icon={EventIcon} to={`/admin/events?id=${value}`} label={data?.name ?? 'Unknown Event'} />
  );
}

/**
 * Team management page for admins.
 */
export default function AdminTeams() {
  const [ searchParams ] = useSearchParams();
  const eventId = searchParams.get('event');

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
      initialState={{
        filter : {
          filterModel : {
            event_id : {
              type : 'equals',
              filter : eventId ?? '',
            },
          },
        },
      }}
      sidebarComponent={TeamSidebar}
    />
  );
}
