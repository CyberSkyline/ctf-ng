import type { ColDef } from 'ag-grid-community';
import { useState } from 'react';
import { Flex } from '@radix-ui/themes';
import AdminGrid from 'components/AdminGrid';
import { useUsers } from '@/hooks/users';
import { ErrorCallout } from 'components/Callouts';
import UserSidebar from './UserSidebar';

/**
 * User management page for admins.
 */
export default function AdminUsers() {
  const { data, error, isLoading } = useUsers();
  const rowData = data?.users ?? [];

  const [ colDefs ] = useState<ColDef<typeof rowData[number]>[]>([
    {
      field : 'name', filter : true, floatingFilter : true, width : 200,
    },
    { field : 'role' },
    { field : 'id' },
    { field : 'registered_at', width : 150, valueFormatter : (params) => new Date(params.value).toLocaleString() },
  ]);

  if (error) {
    return (
      <ErrorCallout>{error.message}</ErrorCallout>
    );
  }

  return (
    <Flex direction="row" gap="4" className="w-full h-full">
      <AdminGrid
        rowData={rowData}
        columnDefs={colDefs}
        loading={isLoading}
        getRowId={(params) => params.data.id.toString()}
      />
      <Flex direction="column" gap="4" height="100%" className="w-128 grow-0 shrink-0 overflow-y-auto" overflowY="auto">
        <UserSidebar />
      </Flex>

    </Flex>
  );
}
