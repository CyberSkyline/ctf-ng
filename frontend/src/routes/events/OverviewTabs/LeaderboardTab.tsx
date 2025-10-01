import { radixTheme } from '@/grid';
import { useLeaderboard } from '@/hooks/events';
import { useMyTeamScore } from '@/hooks/scoring';
import { Container, Flex } from '@radix-ui/themes';
import { AgGridReact } from 'ag-grid-react';
import { ErrorCallout } from 'components/Callouts';
import Statistic from 'components/Statistic';
import { useParams } from 'react-router';

export default function LeaderboardTab() {
  const { idEvent } = useParams();
  const { data : myTeamScore, error : myTeamScoreError } = useMyTeamScore(Number(idEvent));
  const { data : leaderboard, error : leaderboardError } = useLeaderboard(Number(idEvent));

  return (
    <Container size="4">
      <Flex direction="column" gap="3">
        <Flex direction="row" gap="3">
          <Statistic value={myTeamScore?.points ?? ''} label="Your Score" description={`Last updated ${myTeamScore?.last_update.toLocaleString()}`} />
        </Flex>

        {myTeamScoreError && <ErrorCallout>{myTeamScoreError.message}</ErrorCallout>}
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
              sort : 'desc',
              cellClass : 'tabular-nums',
            },
            {
              headerName : 'Last Updated',
              field : 'last_update',
              valueFormatter : ({ value }) => value.toLocaleString(),
            },
          ]}
          theme={radixTheme}
          pagination
          paginationPageSize={20}
          domLayout="autoHeight"
        />
      </Flex>
    </Container>
  );
}
