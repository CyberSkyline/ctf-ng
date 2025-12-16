import { radixTheme } from '@/grid';
import { useEventFeedback } from '@/hooks/feedback';
import type { Event, Feedback } from '@/types';
import { Flex, Spinner } from '@radix-ui/themes';
import type { ColDef } from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';

const colDefs = [
  {
    field : 'user_name',
    headerName : 'User',
    sortable : true,
    filter : true,
    width : 200,
  },
  {
    field : 'feedback_data.role',
    headerName : 'NICE Role',
    sortable : false,
    filter : true,
    width : 200,
  },
  {
    field : 'feedback_data.education',
    headerName : 'Education',
    sortable : false,
    filter : true,
    width : 200,
  },
  {
    field : 'feedback_data.cyber_experience',
    headerName : 'Years of Experience',
    sortable : false,
    filter : true,
    width : 200,
  },
  {
    field : 'feedback_data.participation_reason',
    headerName : 'Participation Reason',
    sortable : false,
    filter : true,
    width : 300,
  },
  {
    field : 'feedback_data.participation_again',
    headerName : 'Future Participation',
  },
  {
    field : 'feedback_data.additional_feedback',
    headerName : 'Other Feedback',
    sortable : false,
    filter : true,
    minWidth : 400,
    autoHeight : true,
    wrapText : true,
    cellStyle : { lineHeight : '20px', paddingTop : '8px', paddingBottom : '8px' },
  },
] as ColDef<Feedback>[];

export default function EventFeedbackTab({ event }: {event: Event}) {
  const { data : feedback, isLoading } = useEventFeedback(event.id);

  return (
    <Flex direction="column" gap="3" className="h-full">
      <AgGridReact
        columnDefs={colDefs}
        rowData={feedback}
        loading={isLoading}
        loadingOverlayComponent={Spinner}
        theme={radixTheme}
      />
    </Flex>
  );
}
