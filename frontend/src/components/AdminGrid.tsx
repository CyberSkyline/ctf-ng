import useAdminGridDatasource from '@/hooks/grid';
import { radixTheme } from '@/grid';
import { base64ToUtf8, utf8ToBase64 } from '@/util';
import { Flex, Skeleton, Spinner } from '@radix-ui/themes';
import type { ColDef, GridApi, GridOptions } from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import {
  useCallback,
  useEffect,
  useState,
  type ReactNode,
} from 'react';
import { useSearchParams } from 'react-router';
import useSWR, { mutate } from 'swr';

type AdminGridProps<T> = {
  columnDefs: ColDef<T>[];
  loading?: boolean;
  toolbar?: ReactNode;
  getRowId: (params: { data: T }) => string;
  gridOptions?: GridOptions;
  stopCellSelection?: string[]; // colIds of cells
} & (
  // client-side: rows supplied directly
  | { rowData: T[]; collectionKey?: never; sidebarComponent?: React.ComponentType<{ entity: T }> }
  // server-side: rows come from collectionKey
  | { collectionKey: string; rowData?: never; sidebarComponent?: React.ComponentType<{ selectedId: number }> }
);

/**
 * Skeleton for AG grid cells that are still loading.
 */
function LoadingCell() {
  return (
    <Flex align="center" className="w-full h-full">
      <Skeleton><div className="w-full" /></Skeleton>
    </Flex>
  );
}

/**
 * Wrapper around AgGridReact with common functionality for all admin grids.
 */
export default function AdminGrid<T>({
  rowData,
  collectionKey,
  columnDefs,
  loading = false,
  sidebarComponent,
  toolbar,
  getRowId,
  gridOptions,
  stopCellSelection,
}: AdminGridProps<T>) {
  const [ searchParams, setSearchParams ] = useSearchParams();
  const selectedId = searchParams.get('id');

  const [ gridApi, setGridApi ] = useState<GridApi<T> | null>(null);

  const datasource = useAdminGridDatasource<T>(collectionKey);

  // Refresh grid blocks when SWR mutation for the given key occurs
  useSWR(collectionKey ?? null, () => true, {
    onSuccess : () => gridApi?.refreshInfiniteCache(),
  });

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
        gridApi.setFilterModel(JSON.parse(base64ToUtf8(filterModel)));
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
            return JSON.parse(base64ToUtf8(filter));
          } catch {
            return {};
          }
        }
        return {};
      })(),
    },
  };

  const rowModelProps = collectionKey
    ? { rowModelType : 'infinite' as const, datasource, cacheBlockSize : 100 }
    : { rowData };

  const Sidebar = sidebarComponent as React.ComponentType<{ entity?: T; selectedId?: number }> | undefined;

  return (
    <Flex direction="row" gap="3" className="w-full h-full">
      <Flex direction="column" gap="3" className="grow" role="main">
        {toolbar}
        <AgGridReact
          key="admin-grid"
          theme={radixTheme}
          {...rowModelProps}
          columnDefs={columnDefs}
          rowSelection={{
            mode : 'singleRow',
            checkboxes : true,
          }}
          loading={loading}
          loadingOverlayComponent={Spinner}
          defaultColDef={{
            // infinite-model rows render before their block loads (data == null) -> skeleton
            cellRendererSelector : (p) => (p.data == null ? { component : LoadingCell } : undefined),
          }}
          getRowId={getRowId}
          onCellClicked={(e) => {
            if (!stopCellSelection?.includes(e.column.getColId())) {
              e.node.setSelected(true);
            }
          }}
          onRowDoubleClicked={(event) => {
            if (event.node.isSelected()) {
              event.node.setSelected(false);
            }
          }}
          onRowSelected={(event) => {
            if (event.node.isSelected() && event.node.id && event.node.id !== selectedId) {
              // Heat the sidebar's cache so its by-id fetch resolves instantly.
              if (collectionKey && event.node.data) {
                mutate(`${collectionKey}/${event.node.id}`, event.node.data, { revalidate : false });
              }
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
          onRowDataUpdated={updateSelection} // client model
          onModelUpdated={updateSelection} // infinite model
          onGridReady={(params) => {
            setGridApi(params.api);
          }}
          onFilterChanged={(params) => {
          // Update the URL when grid filter model changes
            const filterModel = params.api.getFilterModel();
            if (Object.keys(filterModel).length > 0) {
              const filterString = utf8ToBase64(JSON.stringify(filterModel));

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
      </Flex>
      {Sidebar && (collectionKey
        ? selectedId && (
          <Sidebar selectedId={Number(selectedId)} key={selectedId} />
        )
        : selectedData && (
          <Sidebar entity={selectedData} key={selectedId} />
        ))}
    </Flex>
  );
}
