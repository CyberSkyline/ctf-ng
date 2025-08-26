import { useAllUsers } from '@/hooks/users';
import type { User } from '@/types';
import type { ColDef } from 'ag-grid-community';
import AdminGrid from 'components/AdminGrid';
import { ErrorCallout } from 'components/Callouts';
import RoleBadge from 'components/RoleBadge';
import UserSidebar from './UserSidebar';

const colDefs: ColDef<User>[] = [
  {
    field : 'id',
    width : 100,
    headerName : 'ID',
    filter : true,
    floatingFilter : true,
  },
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
    field : 'roles',
    cellRenderer : ({ value }: {value: string[]}) => value.map((role) => (
      <>
        <RoleBadge key={role} value={role} />
        &nbsp;
      </>
    )),
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
];

/**
 * User management page for admins.
 */
export default function AdminUsers() {
  const { data, error, isLoading } = useAllUsers();
  const rowData = data ?? [];

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
