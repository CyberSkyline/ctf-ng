import { COLOR_INFO } from '@/constants';
import { radixTheme } from '@/grid';
import type { Attempt } from '@/types';
import { Button } from '@radix-ui/themes';
import type { ColDef } from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import Modal from 'components/Modal';
import TeamActivityTypeBadge from 'components/TeamActivityTypeBadge';
import { TbHistory } from 'react-icons/tb';

const colDefs: ColDef<Attempt>[] = [
  {
    headerName : 'Type',
    cellRenderer : TeamActivityTypeBadge,
    width : 120,
    filterParams : {
      defaultOption : 'startsWith',
    },
    filterValueGetter : ({ data }) => {
      if (!data) return null;
      return data.is_correct ? 'Correct' : 'Incorrect';
    },
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'timestamp',
    headerName : 'Date',
    width : 200,
    valueFormatter : (params) => params.value.toLocaleString(),
    sort : 'desc',
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'question_name',
    headerName : 'Question',
    width : 100,
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'submission',
    headerName : 'Submission',
    flex : 1,
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'user_name',
    headerName : 'User',
    width : 120,
    filter : true,
    floatingFilter : true,
  },
];

export default function HistoryModal({ isTeam, attempts }: {isTeam: boolean, attempts: Attempt[]}) {
  return (
    <Modal
      title="History"
      description={`Your ${isTeam ? 'team\'s ' : ''}past activity for this challenge.`}
      trigger={(
        <Button variant="ghost" color={COLOR_INFO} className="!m-0">
          <TbHistory />
          History
        </Button>
      )}
      className="!max-w-4xl"
    >
      <div className="h-128">
        <AgGridReact
          rowData={attempts}
          columnDefs={colDefs}
          theme={radixTheme}
        />
      </div>
    </Modal>
  );
}
