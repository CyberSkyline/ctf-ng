import { radixTheme } from '@/grid';
import { Flex, Spinner } from '@radix-ui/themes';
import type {
  ColDef,
  GridApi,
  GridOptions,
  TData,
} from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import { useCallback, useEffect, useState } from 'react';
import { useSearchParams } from 'react-router';

/**
 * Wrapper around AgGridReact with common functionality for all admin grids.
 */
export default function AdminGrid<T>({
  rowData,
  columnDefs,
  loading = false,
  sidebarComponent : Sidebar,
  getRowId,
  gridOptions,
}: {
  rowData: T[];
  columnDefs: ColDef<T>[];
  loading?: boolean;
  sidebarComponent?: React.ComponentType<{entity: T}>;
  getRowId: (params: { data: T }) => string;
  gridOptions?: GridOptions<TData>
}) {
  const [ searchParams, setSearchParams ] = useSearchParams();
  const selectedId = searchParams.get('id');

  const [ gridApi, setGridApi ] = useState<GridApi<T> | null>(null);

  const [ selectedData, setSelectedData ] = useState<T | null>(null);

  const updateSelection = useCallback(() => {
    if (!gridApi) return;
    if (selectedId) {
      const node = gridApi.getRowNode(selectedId);
      node?.setSelected(true, true);
      setSelectedData(node?.data ?? null);
    } else {
      gridApi.deselectAll();
      setSelectedData(null);
    }
  }, [ gridApi, selectedId ]);

  // If the selected ID changes in the URL, update the selection.
  // This will also set the selected data object based on the selected row data.
  useEffect(() => {
    updateSelection();
  }, [ updateSelection ]);

  // Update grid filter model when URL changes
  useEffect(() => {
    if (!gridApi) return;
    if (searchParams.has('filter')) {
      const filterModel = searchParams.get('filter')!;
      try {
        gridApi.setFilterModel(JSON.parse(atob(filterModel)));
      } catch {
        // If parsing fails, reset filters
        gridApi.setFilterModel({});
      }
    } else {
      gridApi.setFilterModel({});
    }
  }, [ gridApi, searchParams ]);

  // Use filter model from the URL to set initial filter state
  const initialState = {
    filter : {
      filterModel : (() => {
        const filter = searchParams.get('filter');
        if (filter) {
          try {
            return JSON.parse(atob(filter));
          } catch {
            return {};
          }
        }
        return {};
      })(),
    },
  };

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
        onRowDoubleClicked={(event) => {
          if (event.node.isSelected()) {
            event.node.setSelected(false);
          }
        }}
        onRowSelected={(event) => {
          if (event.node.isSelected() && event.node.id && event.node.id !== selectedId) {
            setSearchParams((prev) => {
              prev.set('id', event.node.id!);
              return prev;
            });
          }
          if (event.api.getSelectedNodes().length === 0 && selectedId) {
            setSearchParams((prev) => {
              prev.delete('id');
              return prev;
            });
          }
        }}
        onRowDataUpdated={updateSelection} // ensure selection is accurate when grid rows load
        onGridReady={(params) => {
          setGridApi(params.api);
        }}
        onFilterChanged={(params) => {
          // Update the URL when grid filter model changes
          const filterModel = params.api.getFilterModel();
          if (Object.keys(filterModel).length > 0) {
            const filterString = btoa(JSON.stringify(filterModel));

            // don't double nav if the filter won't change
            if (searchParams.get('filter') === filterString) return;

            setSearchParams((prev) => {
              prev.set('filter', filterString);
              return prev;
            });
          } else {
            if (!searchParams.has('filter')) return;

            setSearchParams((prev) => {
              prev.delete('filter');
              return prev;
            });
          }
        }}
        initialState={initialState}
        className="w-full h-full grow"
        gridOptions={gridOptions}
      />
      {Sidebar && selectedData && (
        <Sidebar entity={selectedData} key={selectedId} />
      )}
    </Flex>
  );
}
