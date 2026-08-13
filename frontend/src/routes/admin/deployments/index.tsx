import type { Deployment } from '@/types';
import { Flex } from '@radix-ui/themes';
import type { ColDef } from 'ag-grid-community';
import AdminGrid from 'components/AdminGrid';
import DeploymentSidebar from './DeploymentSidebar';

// specify types explicitly since there's no rowData to infer from
const colDefs: ColDef<Deployment>[] = [
  {
    field : 'challenge_name',
    headerName : 'Challenge',
    cellDataType : 'text',
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'team_name',
    headerName : 'Team',
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
  },
  {
    field : 'containers',
    cellDataType : 'number',
    filter : true,
    floatingFilter : true,
  },
];

/**
 * Admin page to manage challenge networks/containers.
 * The datagrid will list full challenge deployments/networks with aggregate stats,
 * and selecting one will show the individual containers within the deployment.
 */
export default function AdminDeployments() {
  return (
    <Flex direction="row" gap="4" className="h-full w-full">
      <title>Admin Deployments</title>
      <AdminGrid
        collectionKey="/admin/container"
        columnDefs={colDefs}
        getRowId={(params) => params.data.id.toString()}
        sidebarComponent={DeploymentSidebar}
      />
    </Flex>
  );
}
