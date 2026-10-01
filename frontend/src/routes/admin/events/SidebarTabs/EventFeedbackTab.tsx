import { radixTheme } from '@/grid';
import { useEventFeedback } from '@/hooks/feedback';
import type { Event, Feedback } from '@/types';
import {
  Button,
  Flex,
  Spinner,
  Text,
  Tooltip,
} from '@radix-ui/themes';
import type { ColDef } from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import { useRef } from 'react';
import { TbInfoCircle } from 'react-icons/tb';

const colDefs = [
  {
    field : 'user_id',
    headerName : 'User ID',
    hide : true,
  },
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
    field : 'feedback_data.difficulty_rating',
    headerName : 'Difficulty Rating',
  },
  {
    field : 'feedback_data.relevancy_rating',
    headerName : 'Relevancy Rating',
  },
  {
    field : 'feedback_data.engagement_rating',
    headerName : 'Engagement Rating',
  },
  {
    field : 'feedback_data.thoughts',
    headerName : 'Thoughts',
    sortable : false,
    filter : true,
    minWidth : 400,
    autoHeight : true,
    wrapText : true,
    cellStyle : { lineHeight : '20px', paddingTop : '8px', paddingBottom : '8px' },
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

  // Historical questions. Keeping hidden for export functionality.
  {
    field : 'feedback_data.education',
    headerName : 'Education',
    hide : true,
  },
] as ColDef<Feedback>[];

export default function EventFeedbackTab({ event }: {event: Event}) {
  const gridRef = useRef<AgGridReact>(null);
  const { data : feedback, isLoading } = useEventFeedback(event.id);

  const exportCsv = () => {
    if (!gridRef.current) return;

    gridRef.current.api.exportDataAsCsv({
      fileName : `${new Date().toISOString().slice(0, 10)} - ${event.name} Feedback.csv`,
      allColumns : true,
    });
  };

  return (
    <Flex direction="column" gap="3" className="h-full">
      <Flex justify="end">
        <Flex align="center" gap="1">
          <Tooltip content="This csv will include any historical data that is not present in the table.">
            <button type="button">
              <Text color="gray">
                <TbInfoCircle aria-label="More info" />
              </Text>
            </button>
          </Tooltip>
          <Button
            onClick={exportCsv}
          >
            Download CSV
          </Button>
        </Flex>
      </Flex>
      <AgGridReact
        ref={gridRef}
        columnDefs={colDefs}
        rowData={feedback}
        loading={isLoading}
        loadingOverlayComponent={Spinner}
        theme={radixTheme}
      />
    </Flex>
  );
}
