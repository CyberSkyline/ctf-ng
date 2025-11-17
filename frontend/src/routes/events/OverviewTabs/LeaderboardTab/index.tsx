import { radixTheme } from '@/grid';
import { useLeaderboard } from '@/hooks/events';
import { Container, Flex, Spinner } from '@radix-ui/themes';
import { AgGridReact } from 'ag-grid-react';
import { ErrorCallout } from 'components/Callouts';
import { useParams } from 'react-router';
import TeamPerformance from './TeamPerformance';

export default function LeaderboardTab() {
  const { idEvent } = useParams();
  const { data : leaderboard, error : leaderboardError } = useLeaderboard(Number(idEvent));

  return (
    <Container size="4">
      <Flex direction="column" gap="3">
        <TeamPerformance eventId={Number(idEvent)} />

        {leaderboardError && <ErrorCallout>{leaderboardError.message}</ErrorCallout>}

        <AgGridReact
          rowData={leaderboard}
          columnDefs={[
            {
              headerName : '#',
              valueGetter : (params) => (params.node?.rowIndex != null ? params.node.rowIndex + 1 : ''),
              width : 80,
            },
            {
              headerName : 'Team',
              field : 'team_name',
              flex : 1,
            },
            {
              headerName : 'Score',
              field : 'points',
              cellClass : 'tabular-nums',
            },
            {
              headerName : 'Last Updated',
              field : 'last_update',
              valueFormatter : ({ value }) => value.toLocaleString(),
            },
          ]}
          theme={radixTheme}
          defaultColDef={{
            sortable : false, // disable sorting for all columns - server side sort is the source of truth
            lockPinned : true,
            suppressMovable : true,
          }}
          pagination
          paginationPageSize={20}
          domLayout="autoHeight"
          loadingOverlayComponent={Spinner}
        />
      </Flex>
    </Container>
  );
}
