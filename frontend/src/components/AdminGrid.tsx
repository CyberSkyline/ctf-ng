import { radixTheme } from '@/grid';
import { Flex, Spinner } from '@radix-ui/themes';
import type { ColDef, GridState } from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import { useState } from 'react';
import { useSearchParams } from 'react-router';

/**
 * Wrapper around AgGridReact with common functionality for all admin grids.
 */
export default function AdminGrid<T>({
  rowData,
  columnDefs,
  initialState,
  loading = false,
  sidebarComponent : Sidebar,
  getRowId,
}: {
    rowData: T[];
    columnDefs: ColDef<T>[];
    initialState?: GridState;
    loading?: boolean;
    sidebarComponent?: React.ComponentType<{entity: T}>;
    getRowId: (params: { data: T }) => string;
}) {
  const [ searchParams, setSearchParams ] = useSearchParams();
  const selectedId = searchParams.get('id');

  const [ selectedData, setSelectedData ] = useState<T | null>(null);

  return (
    <Flex direction="row" gap="4" className="w-full h-full">
      <AgGridReact
        key="admin-grid"
        theme={radixTheme}
        rowData={rowData}
        columnDefs={columnDefs}
        rowSelection={{
          mode : 'singleRow',
          checkboxes : true,
          enableClickSelection : true,
        }}
        loading={loading}
        loadingOverlayComponent={Spinner}
        getRowId={getRowId}
        onRowSelected={(event) => {
          if (event.node.isSelected() && event.node.id && event.node.id !== selectedId) {
            setSearchParams((prev) => {
              prev.set('id', event.node.id!);
              return prev;
            });
            setSelectedData(event.data ?? null);
          }
          if (event.api.getSelectedNodes().length === 0) {
            setSearchParams((prev) => {
              prev.delete('id');
              return prev;
            });
            setSelectedData(null);
          }
        }}
        onRowDataUpdated={(params) => {
          if (selectedId) {
            const node = params.api.getRowNode(selectedId);
            node?.setSelected(true);
            setSelectedData(node?.data ?? null);
          }
        }}
        initialState={initialState}
        className="w-full h-full grow"
      />
      {Sidebar && selectedData && (
        <Sidebar entity={selectedData} key={selectedId} />
      )}
    </Flex>
  );
}
