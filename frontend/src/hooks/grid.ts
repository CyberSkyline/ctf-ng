import { apiFetcher } from '@/fetchers';
import type { PaginatedResponse } from '@/types';
import { utf8ToBase64 } from '@/util';
import type { IDatasource, IGetRowsParams } from 'ag-grid-community';
import { useMemo } from 'react';

/**
 * ag-grid infinite-row-model datasource for a paginated admin collection.
 * Serializes block range + sort/filter model to query params (filterModel
 * base64-encoded per the URL scheme) and fetches via apiFetcher.
 */
export default function useAdminGridDatasource<T>(collectionKey: string | undefined): IDatasource | undefined {
  return useMemo<IDatasource | undefined>(() => {
    if (!collectionKey) return undefined;
    return {
      getRows : async (params: IGetRowsParams) => {
        const search = new URLSearchParams({
          startRow : params.startRow.toString(),
          endRow : params.endRow.toString(),
          sortModel : JSON.stringify(params.sortModel),
        });
        if (Object.keys(params.filterModel).length > 0) {
          search.set('filterModel', utf8ToBase64(JSON.stringify(params.filterModel)));
        }

        try {
          const { rows, lastRow } = await apiFetcher(
            `${collectionKey}?${search}`,
          ) as PaginatedResponse<T>;
          params.successCallback(rows, lastRow);
        } catch {
          params.failCallback();
        }
      },
    };
  }, [ collectionKey ]);
}
