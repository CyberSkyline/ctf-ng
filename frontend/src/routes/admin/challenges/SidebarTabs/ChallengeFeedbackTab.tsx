import { radixTheme } from '@/grid';
import { useChallengeFeedback } from '@/hooks/feedback';
import type { Challenge, Feedback } from '@/types';
import {
  Button,
  Flex,
  Spinner,
  Text,
  Tooltip,
} from '@radix-ui/themes';
import type { ColDef } from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import { ErrorCallout } from 'components/Callouts';
import Statistic from 'components/Statistic';
import { useMemo, useRef } from 'react';
import { TbInfoCircle } from 'react-icons/tb';

const colDefs = [
  {
    field : 'user_id',
    headerName : 'User ID',
  },
  {
    field : 'user_name',
    headerName : 'User',
    sortable : true,
    filter : true,
    width : 200,
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

  // Historical fields hidden and only used for csv download
  {
    field : 'feedback_data.difficulty',
    headerName : 'Difficulty',
    hide : true,
  },
  {
    field : 'feedback_data.quality',
    headerName : 'Quality',
    hide : true,
  },
  {
    field : 'feedback_data.what_liked',
    headerName : 'What Liked',
    hide : true,
  },
  {
    field : 'feedback_data.how_to_improve',
    headerName : 'How to Improve',
    hide : true,
  },
] as ColDef<Feedback>[];

export default function ChallengeFeedbackTab({ challenge }: {challenge: Challenge}) {
  const gridRef = useRef<AgGridReact>(null);
  const { data : feedback, isLoading, error } = useChallengeFeedback(challenge.event_id, challenge.id);

  const averages = useMemo(() => {
    if (!feedback || feedback.length === 0) {
      return { averageDifficulty : 0, averageQuality : 0 };
    }

    // Filter only entries with a valid number for difficulty
    const difficultyEntries = feedback.filter(
      (entry) => typeof entry.feedback_data?.difficulty === 'number',
    );
    const totalDifficulty = difficultyEntries.reduce(
      (sum, entry) => sum + (entry.feedback_data.difficulty as number),
      0,
    );
    const averageDifficulty = difficultyEntries.length > 0 ? totalDifficulty / difficultyEntries.length : 0;

    // Filter only entries with a valid number for quality
    const qualityEntries = feedback.filter(
      (entry) => typeof entry.feedback_data?.quality === 'number',
    );
    const totalQuality = qualityEntries.reduce(
      (sum, entry) => sum + (entry.feedback_data.quality as number),
      0,
    );
    const averageQuality = qualityEntries.length > 0 ? totalQuality / qualityEntries.length : 0;

    return {
      averageDifficulty,
      averageQuality,
    };
  }, [ feedback ]);

  const exportCsv = () => {
    if (!gridRef.current) return;

    const columnKeys = gridRef.current.api
      .getColumns()
      ?.map((column) => column.getColId());

    gridRef.current.api.exportDataAsCsv({
      fileName : `${new Date().toISOString().slice(0, 10)} - ${challenge.name} Feedback.csv`,
      columnKeys,
    });
  };

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  return (
    <>
      <Flex mb="3" justify="between">
        <Flex gap="3">
          <Statistic label="Average Difficulty" value={averages.averageDifficulty.toFixed(1)} />
          <Statistic label="Average Quality" value={averages.averageQuality.toFixed(1)} />
        </Flex>
        <Flex align="end">
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
      </Flex>
      <AgGridReact
        ref={gridRef}
        columnDefs={colDefs}
        rowData={feedback || []}
        theme={radixTheme}
        loading={isLoading}
        loadingOverlayComponent={Spinner}
      />
    </>
  );
}
