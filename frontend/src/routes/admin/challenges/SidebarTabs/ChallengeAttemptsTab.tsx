import { TeamIcon, UserIcon } from '@/constants';
import { radixTheme } from '@/grid';
import { useAdminChallengeAttempts } from '@/hooks/challenge';
import type { Attempt } from '@/types';
import { Spinner } from '@radix-ui/themes';
import { AgGridReact, type CustomCellRendererProps } from 'ag-grid-react';
import { ErrorCallout } from 'components/Callouts';
import DeleteAttemptModal from 'components/DeleteAttemptModal';
import Entity from 'components/Entity';

export default function ChallengeAttemptsTab({ challengeId }: {challengeId: number}) {
  const { data : attempts, isLoading, error } = useAdminChallengeAttempts(challengeId);

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  return (
    <AgGridReact
      columnDefs={[
        {
          field : 'timestamp',
          headerName : 'Timestamp',
          minWidth : 180,
          cellDataType : 'dateString',
          sortable : true,
          filter : true,
          pinned : 'left',
          sort : 'desc',
        },
        {
          field : 'team_name',
          headerName : 'Team',
          minWidth : 150,
          sortable : true,
          filter : true,
          cellRenderer : Entity,
          cellRendererParams : (params: CustomCellRendererProps<Attempt>) => ({
            label : params.value,
            icon : TeamIcon,
            to : `/admin/teams?id=${params.data!.team_id}`,
          }),
        },
        {
          field : 'user_name',
          headerName : 'User',
          flex : 1,
          minWidth : 150,
          filter : true,
          cellRenderer : Entity,
          cellRendererParams : (params: CustomCellRendererProps<Attempt>) => ({
            label : params.value,
            icon : UserIcon,
            to : `/admin/users?id=${params.data!.user_id}`,
          }),
        },
        {
          field : 'question_name', headerName : 'Question', flex : 1, minWidth : 150, sortable : true, filter : true,
        },
        {
          field : 'submission', headerName : 'Submission', flex : 1, minWidth : 150, sortable : true, filter : true,
        },
        {
          field : 'is_correct', headerName : 'Correct', width : 100, sortable : true, filter : true,
        },
        {
          headerName : 'Actions',
          type : 'rightAligned',
          pinned : 'right',
          width : 100,
          cellRenderer : DeleteAttemptModal,
          cellRendererParams : ({ data }: {data: Attempt}) => ({ attempt : data }),
        },
      ]}
      rowData={attempts || []}
      theme={radixTheme}
      loading={isLoading}
      loadingOverlayComponent={Spinner}
    />
  );
}
