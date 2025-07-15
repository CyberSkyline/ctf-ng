import AdminGrid from 'components/AdminGrid';
import { useAllUsers } from '@/hooks/users';
import { ErrorCallout } from 'components/Callouts';
import RoleBadge from 'components/RoleBadge';
import type { ColDef } from 'ag-grid-community';
import UserSidebar from './UserSidebar';

/**
 * User management page for admins.
 */
export default function AdminUsers() {
  const { data, error, isLoading } = useAllUsers();
  const rowData = data ?? [];

  const colDefs: ColDef<typeof rowData[number]>[] = [
    {
      field : 'name',
      filter : true,
      floatingFilter : true,
      width : 200,
    },
    {
      field : 'email',
      filter : true,
      floatingFilter : true,
      width : 250,
    },
    {
      field : 'role',
      cellRenderer : RoleBadge,
      filter : true,
      floatingFilter : true,
      width : 120,
    },
    {
      field : 'registered_at',
      headerName : 'Registered At',
      width : 220,
      valueFormatter : (params) => params.value && params.value.toLocaleString(),
      filter : true,
      floatingFilter : true,
    },
    {
      field : 'id',
      width : 100,
      headerName : 'ID',
      filter : true,
      floatingFilter : true,
    },
  ];

  if (error) {
    return (
      <ErrorCallout>{error.message}</ErrorCallout>
    );
  }

  return (
    <AdminGrid
      rowData={rowData}
      columnDefs={colDefs}
      loading={isLoading}
      getRowId={(params) => params.data.id.toString()}
      sidebarComponent={UserSidebar}
    />
  );
}
