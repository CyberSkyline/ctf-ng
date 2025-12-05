import { radixTheme } from '@/grid';
import { useChallengeFeedback } from '@/hooks/feedback';
import type { Challenge, Feedback } from '@/types';
import { Flex, Spinner } from '@radix-ui/themes';
import type { ColDef } from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import { ErrorCallout } from 'components/Callouts';
import Statistic from 'components/Statistic';
import { startCase } from 'lodash';
import { useMemo } from 'react';

export default function ChallengeFeedbackTab({ challenge }: {challenge: Challenge}) {
  const { data : feedback, isLoading, error } = useChallengeFeedback(challenge.event_id, challenge.id);

  // Figure out coldefs based on the shape of data.feedback_data. data may be jagged, have to check all rows

  const colDefs = useMemo(() => {
    const defs = [ {
      field : 'user_id',
      headerName : 'User',
      minWidth : 180,
      sortable : true,
      filter : true,
    } ] as ColDef<Feedback>[];

    if (feedback && feedback.length > 0) {
      const allKeys = new Set<string>();
      feedback.forEach((row) => {
        Object.keys(row.feedback_data).forEach((key) => allKeys.add(key));
      });

      allKeys.forEach((key) => {
        defs.push({
          field : `feedback_data.${key}`,
          headerName : startCase(key),
          sortable : true,
          filter : true,
          wrapText : true,
          autoHeight : true,
        });
      });
    }

    return defs;
  }, [ feedback ]);

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  return (
    <>
      <Flex direction="row" mb="3" gap="3">
        <Statistic label="Average Difficulty" value={Number(6).toFixed(1)} />
        <Statistic label="Average Quality" value={Number(6).toFixed(1)} />
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
