import { radixTheme } from '@/grid';
import { useChallengeFeedback } from '@/hooks/feedback';
import type { Challenge, Feedback } from '@/types';
import { Flex, Spinner } from '@radix-ui/themes';
import type { ColDef } from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import { ErrorCallout } from 'components/Callouts';
import Statistic from 'components/Statistic';
import { useMemo } from 'react';

const colDefs = [
  {
    field : 'user_name',
    headerName : 'User',
    sortable : true,
    filter : true,
    width : 200,
  },
  {
    field : 'feedback_data.difficulty',
    headerName : 'Difficulty',
    sortable : true,
    filter : true,
    width : 90,
  },
  {
    field : 'feedback_data.quality',
    headerName : 'Quality',
    sortable : true,
    filter : true,
    width : 90,
  },
  {
    field : 'feedback_data.what_liked',
    headerName : 'What Liked',
    sortable : false,
    filter : true,
    minWidth : 400,
    autoHeight : true,
    wrapText : true,
    cellStyle : { lineHeight : '20px', paddingTop : '8px', paddingBottom : '8px' },
  },
  {
    field : 'feedback_data.how_to_improve',
    headerName : 'How to Improve',
    sortable : false,
    filter : true,
    minWidth : 400,
    autoHeight : true,
    wrapText : true,
    cellStyle : { lineHeight : '20px', paddingTop : '8px', paddingBottom : '8px' },
  },
] as ColDef<Feedback>[];

export default function ChallengeFeedbackTab({ challenge }: {challenge: Challenge}) {
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

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  return (
    <>
      <Flex direction="row" mb="3" gap="3">
        <Statistic label="Average Difficulty" value={averages.averageDifficulty.toFixed(1)} />
        <Statistic label="Average Quality" value={averages.averageQuality.toFixed(1)} />
      </Flex>
      <AgGridReact
        columnDefs={colDefs}
        rowData={feedback || []}
        theme={radixTheme}
        loading={isLoading}
        loadingOverlayComponent={Spinner}

      />
    </>
  );
}
