import {
  Box,
  Button,
  Flex,
  Heading,
} from '@radix-ui/themes';
import { deleteAnnouncement, useAnnouncements } from '@/hooks/announcements';
import { ErrorCallout } from 'components/Callouts';
import Entity from 'components/Entity';
import { UserIcon, COLOR_NEGATIVE } from '@/constants';
import type { ColDef, ICellRendererParams } from 'ag-grid-community';
import type { Announcement } from '@/types';
import { AgGridReact, type CustomCellRendererProps } from 'ag-grid-react';
import { radixTheme } from '@/grid';
import { useCallback, useMemo, useState } from 'react';
import CreateAnnoucementModal from './CreateAnnouncementModal';

function ActionCell({ announcementId, deleteAction }: {announcementId: number, deleteAction: (id: number) => void}) {
  return (
    <Button
      size="1"
      color={COLOR_NEGATIVE}
      onClick={() => deleteAction(announcementId)}
    >
      Delete
    </Button>
  );
}

export default function AdminAnnouncements() {
  const [ deleteError, setDeleteError ] = useState<string | null>(null);
  const { data, error, isLoading } = useAnnouncements();
  const rowData = data ?? [];

  const deleteAction = useCallback((id : number) => {
    setDeleteError(null);
    deleteAnnouncement(id).catch((err) => {
      setDeleteError(err.message);
    });
  }, [ setDeleteError ]);

  const colDefs: ColDef<Announcement>[] = useMemo(() => ([
    {
      field : 'id',
      headerName : 'ID',
    }, {
      field : 'title',
      headerName : 'Title',
    }, {
      field : 'message',
      headerName : 'Message',
    }, {
      field : 'sender_name',
      headerName : 'Sender',
      cellRenderer : Entity,
      cellRendererParams : (params: ICellRendererParams<Announcement>) => ({
        icon : UserIcon,
        label : params.data?.sender_name ?? `UNKNOWN (${params.data?.sender_id})`,
        to : `/admin/users?id=${params.data?.sender_id}`,
      }),
    }, {
      field : 'created_at',
      headerName : 'Created Date',
      valueFormatter : (params) => params.value?.toLocaleString(),
    }, {
      field : 'expires_at',
      headerName : 'Expiration Date',
      valueFormatter : (params) => params.value?.toLocaleString(),
    }, {
      field : 'type',
      headerName : 'type',
    }, {
      headerName : 'Actions',
      cellStyle : {
        display : 'flex ',
        alignItems : 'center ',
      },
      cellRenderer : ActionCell,
      cellRendererParams : (params: CustomCellRendererProps<Announcement>) => ({
        announcementId : params.data?.id,
        deleteAction,
      }),
    },
  ]), [ deleteAction ]);

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  return (
    <Flex gap="3" direction="column">
      <title>Admin Announcements</title>
      <Heading size="7">Announcements</Heading>
      {deleteError && <ErrorCallout>{deleteError}</ErrorCallout>}
      <Box maxWidth="200px">
        <CreateAnnoucementModal />
      </Box>
      <AgGridReact
        theme={radixTheme}
        rowData={rowData}
        columnDefs={colDefs}
        domLayout="autoHeight"
        loading={isLoading}
      />
    </Flex>
  );
}
