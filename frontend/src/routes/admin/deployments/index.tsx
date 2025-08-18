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

function TeamCellRenderer({ data }: {data: Deployment}) {
  return <Entity icon={TeamIcon} label={data.team_name} to={`/admin/teams?id=${data.team}`} />;
}

function ChallengeCellRenderer({ data }: {data: Deployment}) {
  return <Entity icon={ChallengeIcon} label={data.challenge_name} to={`/admin/events?id=${data.event_id}`} />;
}

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
      cellRenderer : ChallengeCellRenderer,
      filter : true,
      floatingFilter : true,
    },
    {
      field : 'team',
      headerName : 'Team',
      cellRenderer : TeamCellRenderer,
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
