import { useAllUsers } from '@/hooks/users';
import type { AdminUser } from '@/types';
import type { ColDef } from 'ag-grid-community';
import AdminGrid from 'components/AdminGrid';
import { ErrorCallout } from 'components/Callouts';
import RoleBadge from 'components/RoleBadge';
import { Fragment } from 'react/jsx-runtime';
import { Flex } from '@radix-ui/themes';
import UserSidebar from './UserSidebar';
import CreateUserModal from './CreateUserModal';

const colDefs: ColDef<AdminUser>[] = [
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
    valueFormatter : (params) => params.value.join(', '),
    cellRenderer : ({ value }: {value: string[]}) => value.map((role) => (
      <Fragment key={role}>
        <RoleBadge value={role} />
        &nbsp;
      </Fragment>
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
  {
    field : 'affiliation.name',
    headerName : 'Sponsor',
    filter : true,
    floatingFilter : true,
    width : 200,
  },
  {
    field : 'is_sso',
    headerName : 'SSO',
    width : 100,
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'banned',
    width : 100,
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
    <>
      <title>Admin Users</title>
      <AdminGrid
        rowData={rowData}
        columnDefs={colDefs}
        loading={isLoading}
        getRowId={(params) => params.data.id.toString()}
        sidebarComponent={UserSidebar}
        toolbar={(
          <Flex direction="row" justify="start">
            <CreateUserModal />
          </Flex>
        )}
      />
    </>
  );
}
