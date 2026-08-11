import { radixTheme } from '@/grid';
import { useEvent, useLeaderboard } from '@/hooks/events';
import { useFileList } from '@/hooks/fileuploads';
import type { Score, Sponsor, UploadedFile } from '@/types';
import {
  Container,
  Flex,
  Spinner,
  Tooltip,
} from '@radix-ui/themes';
import { ModuleRegistry, TooltipModule } from 'ag-grid-community';
import { AgGridReact, type CustomCellRendererProps } from 'ag-grid-react';
import { ErrorCallout, WarningCallout } from 'components/Callouts';
import { keyBy, map } from 'lodash';
import { TbInfoCircle } from 'react-icons/tb';
import { useParams } from 'react-router';
import TeamPerformance from './TeamPerformance';

function SponsorCell({ sponsors, lookup }: {sponsors: Sponsor[], lookup: Record<string, UploadedFile>}) {
  return (
    <Flex gap="1" className="pt-px">
      {map(sponsors, ({ logo, name, id }) => {
        let url;
        if (logo) {
          url = lookup[logo]?.download_url;
        }

        return (
          <Tooltip content={name} key={id}>
            {url
              ? <img src={url} alt="" className="h-9 w-9 object-cover" />
              : <TbInfoCircle key={id} className="h-9 w-9 object-cover" />}
          </Tooltip>
        );
      })}
    </Flex>
  );
}

ModuleRegistry.registerModules([
  TooltipModule,
]);

export default function LeaderboardTab() {
  const { idEvent } = useParams();
  const { data : event, error : eventError } = useEvent(Number(idEvent));
  const { data : leaderboard, error : leaderboardError } = useLeaderboard(Number(idEvent));
  const { data : logoList } = useFileList('sponsor-logos', true);
  const files = logoList?.files ?? [];
  const lookup = keyBy(files.filter((f: UploadedFile) => f.filename), 'filename');

  const isIndividual = event?.max_team_size === 1;

  if (eventError) {
    return <ErrorCallout>{eventError.message}</ErrorCallout>;
  }

  return (
    <Container size="4">
      <Flex direction="column" gap="3">
        <TeamPerformance eventId={Number(idEvent)} />

        {leaderboardError
          && (leaderboardError.message.includes('Leaderboard is not available')
            ? <WarningCallout>The leaderboard for this event is currently hidden.</WarningCallout>
            : <ErrorCallout>{leaderboardError.message}</ErrorCallout>
          )}

        {!leaderboardError && event && (
          <AgGridReact
            rowData={leaderboard}
            columnDefs={[
              {
                headerName : '#',
                valueGetter : (params: CustomCellRendererProps<Score>) => (params.node?.rowIndex != null ? params.node.rowIndex + 1 : ''),
                width : 80,
              },
              {
                headerName : isIndividual ? 'Name' : 'Team',
                field : 'team_name',
                flex : 1,
              },
              {
                headerName : 'Sponsors',
                flex : 1,
                cellRenderer : SponsorCell,
                cellRendererParams : (params: CustomCellRendererProps<Score>) => ({
                  sponsors : params.data?.sponsors,
                  lookup,
                }),
              },
              {
                headerName : 'Score',
                field : 'points',
                cellClass : 'tabular-nums',
              },
              {
                headerName : 'Offset of Submission',
                headerTooltip : 'The time lapse between starting the competition and the last correct submission.',
                field : 'last_correct_offset',
                valueFormatter : ({ value }) => new Intl.DurationFormat('en', { style : 'narrow' }).format({
                  hours : Math.floor(value / 3600000),
                  minutes : Math.floor((value % 3600000) / 60000),
                  seconds : Math.floor((value % 60000) / 1000),
                }),
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
            suppressCellFocus
            suppressHeaderFocus
            tooltipShowDelay={500}
          />
        )}
      </Flex>
    </Container>
  );
}
