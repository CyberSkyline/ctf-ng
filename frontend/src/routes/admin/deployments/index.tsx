import { ChallengeIcon, TeamIcon } from '@/constants';
import { useAllDeployments } from '@/hooks/container';
import type { Deployment } from '@/types';
import { Flex } from '@radix-ui/themes';
import type { ColDef } from 'ag-grid-community';
import AdminGrid from 'components/AdminGrid';
import { ErrorCallout } from 'components/Callouts';
import Entity from 'components/Entity';
import EventCellRenderer from 'components/EventCellRenderer';
import DeploymentSidebar from './DeploymentSidebar';

/**
 * Admin page to manage challenge networks/containers.
 * The datagrid will list full challenge deployments/networks with aggregate stats,
 * and selecting one will show the individual containers within the deployment.
 */
export default function AdminDeployments() {
  const { data, error, isLoading } = useAllDeployments();

  const rowData = data ?? [];

  const colDefs: ColDef<typeof rowData[number]>[] = [
    {
      field : 'challenge_id',
      headerName : 'Challenge',
      cellRenderer : Entity,
      cellRendererParams : (params: { data: Deployment }) => ({
        icon : ChallengeIcon,
        label : params.data.challenge_name,
        to : `/admin/events?id=${params.data.event_id}`,
      }),
      filter : true,
      floatingFilter : true,
    },
    {
      field : 'team',
      headerName : 'Team',
      cellRenderer : Entity,
      cellRendererParams : (params: { data: Deployment }) => ({
        icon : TeamIcon,
        label : params.data.team_name,
        to : `/admin/teams?id=${params.data.team}`,
      }),
      filter : true,
      floatingFilter : true,
    },
    {
      field : 'event_id',
      headerName : 'Event',
      cellRenderer : EventCellRenderer,
      filter : true,
      floatingFilter : true,
    },
    { field : 'containers' },
  ];

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
      />
    </Flex>
  );
}
