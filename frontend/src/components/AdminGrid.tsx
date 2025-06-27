import { radixTheme } from '@/grid';
import { Spinner } from '@radix-ui/themes';
import type { ColDef } from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import { useSearchParams } from 'react-router';

/**
 * Wrapper around AgGridReact with common functionality for all admin grids.
 */
export default function AdminGrid<T>({
  rowData,
  columnDefs,
  loading = false,
  getRowId,
}: {
    rowData: T[];
    columnDefs: ColDef<T>[];
    loading?: boolean;
    getRowId: (params: { data: T }) => string;
}) {
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedId = searchParams.get('id');

  return (
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
        }
        if (event.api.getSelectedNodes().length === 0) {
          setSearchParams((prev) => {
            prev.delete('id');
            return prev;
          });
        }
      }}
      onRowDataUpdated={(params) => {
        // Sync the grid selection with what should be selected as new data is loaded
        // to ensure that the selected row is selected once it loads in.
        if (selectedId) {
          params.api.getRowNode(selectedId)?.setSelected(true);
        }
      }}
      className="w-full h-full grow"
    />
  );
}
