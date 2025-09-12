import { ChallengeIcon, EventIcon, TeamIcon } from '@/constants';
import { useAllDeployments } from '@/hooks/container';
import type { Deployment } from '@/types';
import { Flex } from '@radix-ui/themes';
import type { ColDef } from 'ag-grid-community';
import AdminGrid from 'components/AdminGrid';
import { ErrorCallout } from 'components/Callouts';
import Entity from 'components/Entity';
import DeploymentSidebar from './DeploymentSidebar';

const colDefs: ColDef<Deployment>[] = [
  {
    field : 'challenge_name',
    headerName : 'Challenge',
    cellRenderer : Entity,
    cellRendererParams : ({ data } : { data : Deployment }) => ({
      label : data.challenge_name ?? `UNKNOWN (${data.challenge_id})`,
      to : `/admin/events?id=${data.event_id}`,
      icon : ChallengeIcon,
    }),
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'team_name',
    headerName : 'Team',
    cellRenderer : Entity,
    cellRendererParams : (params: { data: { team_name?: string, team_id: number } }) => ({
      icon : TeamIcon,
      label : params.data.team_name ?? `UNKNOWN (${params.data.team_id})`,
      to : `/admin/teams?id=${params.data.team_id}`,
    }),
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
  { field : 'containers' },
];

/**
 * Admin page to manage challenge networks/containers.
 * The datagrid will list full challenge deployments/networks with aggregate stats,
 * and selecting one will show the individual containers within the deployment.
 */
export default function AdminDeployments() {
  const { data, error, isLoading } = useAllDeployments();

  const rowData = data ?? [];

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  return (
    <Flex direction="row" gap="4" className="h-full w-full">
      <AdminGrid
        rowData={rowData}
        columnDefs={colDefs}
        loading={isLoading}
        getRowId={(params) => params.data.id.toString()}
        sidebarComponent={DeploymentSidebar}
        stopCellSelection={[ 'challenge_name', 'team_name', 'event_name' ]}
      />
    </Flex>
  );
}
