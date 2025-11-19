import { useAllDeployments } from '@/hooks/container';
import type { Deployment } from '@/types';
import { Flex } from '@radix-ui/themes';
import type { ColDef } from 'ag-grid-community';
import AdminGrid from 'components/AdminGrid';
import { ErrorCallout } from 'components/Callouts';
import DeploymentSidebar from './DeploymentSidebar';

const colDefs: ColDef<Deployment>[] = [
  {
    field : 'challenge_name',
    headerName : 'Challenge',
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'team_name',
    headerName : 'Team',
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'event_name',
    headerName : 'Event',
    width : 250,
    filter : true,
    floatingFilter : true,
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
      <title>Admin Deployments</title>
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
