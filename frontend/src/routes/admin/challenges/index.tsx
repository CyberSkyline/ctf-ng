import { EventIcon } from '@/constants';
import { useAllChallenges } from '@/hooks/challenge';
import type { Challenge } from '@/types';
import type { ColDef } from 'ag-grid-community';
import type { CustomCellRendererProps } from 'ag-grid-react';
import AdminGrid from 'components/AdminGrid';
import { ErrorCallout } from 'components/Callouts';
import ChallengeIcon from 'components/ChallengeIcon';
import Entity from 'components/Entity';
import ChallengeSidebar from './ChallengeSidebar';

const colDefs: ColDef<Challenge>[] = [
  {
    field : 'id',
    headerName : 'ID',
    width : 80,
  },
  {
    field : 'name',
    cellRenderer : (params: CustomCellRendererProps<Challenge>) => (
      <>
        <ChallengeIcon icon={params.data!.icon} />
        <span className="min-w-0 overflow-hidden text-ellipsis">{params.value}</span>
      </>
    ),
    cellClass : '!flex flex-row items-center gap-1',
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'event_name',
    headerName : 'Event',
    cellRenderer : Entity,
    cellRendererParams : (params: { data: {event_name?: string, event_id: number} }) => ({
      icon : EventIcon,
      label : params.data.event_name ?? `UNKNOWN (${params.data.event_id})`,
      to : `/admin/events?id=${params.data.event_id}`,
    }),
    filter : true,
    floatingFilter : true,
    width : 250,
  },
  {
    field : 'num_questions',
    headerName : 'Questions',
    width : 120,
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'total_points',
    headerName : 'Points',
    width : 120,
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'summary',
    headerName : 'Summary',
    width : 500,
    filter : true,
    floatingFilter : true,
  },
];

export default function AdminChallenges() {
  const { data, error, isLoading } = useAllChallenges();
  const rowData = data ?? [];

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  return (
    <>
      <title>Admin Challenges</title>
      <AdminGrid
        rowData={rowData}
        columnDefs={colDefs}
        loading={isLoading}
        getRowId={(params) => params.data.id.toString()}
        sidebarComponent={ChallengeSidebar}
        stopCellSelection={[ 'event_name' ]}
      />
    </>
  );
}
