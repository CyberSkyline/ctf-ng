import {
  ChallengeIcon,
  COLOR_HINT,
  COLOR_NEGATIVE,
  COLOR_POSITIVE,
  COLOR_WARNING,
  UserIcon,
} from '@/constants';
import { radixTheme } from '@/grid';
import { useTeamAttempts, useTeamHintRedemptions, useTeamManualAwards } from '@/hooks/team';
import type { Attempt, HintRedemption, ManualPointAward } from '@/types';
import { Badge } from '@radix-ui/themes';
import type { ColDef } from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import { ErrorCallout } from 'components/Callouts';
import Entity from 'components/Entity';
import { useMemo } from 'react';

const colDefs: ColDef<Attempt | HintRedemption | ManualPointAward>[] = [
  {
    headerName : 'Type',
    valueGetter : ({ data }) => {
      if (!data) return undefined;
      if ('submission' in data) return 'Attempt';
      if ('hint_preview' in data) return 'Hint';
      if ('reason' in data) return 'Manual';
      return 'Unknown';
    },
    cellRenderer : Badge,
    cellRendererParams : (
      { value, data } : {
        value: 'Attempt' | 'Hint' | 'Manual' | 'Unknown',
        data: Attempt | HintRedemption | ManualPointAward | undefined
      },
    ) => {
      let color;
      switch (value) {
        case 'Attempt':
          color = (data as Attempt).is_correct ? COLOR_POSITIVE : COLOR_NEGATIVE;
          break;
        case 'Hint':
          color = COLOR_HINT;
          break;
        case 'Manual':
          color = COLOR_WARNING;
          break;
        default:
          color = 'gray';
      }

      return {
        children : value.toUpperCase(),
        color,
      };
    },
    width : 100,
    filter : true,
    floatingFilter : true,
    pinned : true,
  },
  {
    field : 'points',
    width : 100,
    filter : true,
    floatingFilter : true,
    pinned : true,
    cellClass : 'tabular-nums text-right',
  },
  {
    field : 'timestamp',
    valueFormatter : ({ value }) => value.toLocaleString(),
    filter : true,
    floatingFilter : true,
    sort : 'desc',
  },
  {
    headerName : 'User',
    valueGetter : ({ data }) => {
      if (!data) return undefined;
      if ('user_id' in data) return data.user_name ?? `MISSING (${data.user_id})`;
      if ('admin_id' in data) return data.admin_name ?? `MISSING (${data.admin_id})`;
      return undefined;
    },
    cellRendererSelector : ({ value, data }) => {
      if (!value || !data) return undefined;

      const id = 'user_id' in data ? data.user_id : data.admin_id;

      return {
        component : Entity,
        params : {
          label : value,
          to : `/admin/users?id=${id}`,
          icon : UserIcon,
        },
      };
    },
    filter : true,
    floatingFilter : true,
  },
  {
    headerName : 'Challenge',
    valueGetter : ({ data }) => {
      if (!data || !('challenge_id' in data)) return undefined; // if no data or it's a manual award
      return data.challenge_name ?? `MISSING (${data.challenge_id})`;
    },
    cellRendererSelector : ({ value, data }) => {
      if (!value || !data || !('challenge_id' in data)) return undefined;

      return {
        component : Entity,
        params : {
          label : value,
          to : `/admin/events?id=${data.event_id}`,
          icon : ChallengeIcon,
        },
      };
    },
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'submission',
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'hint_preview',
    headerName : 'Hint',
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'reason',
    filter : true,
    floatingFilter : true,
  },
];

export default function TeamActivity({ eventId, teamId }: { eventId: number, teamId: number }) {
  const { data : attempts, error : attemptsError, isLoading : attemptsLoading } = useTeamAttempts(eventId, teamId);
  const { data : hintRedemptions, error : hintsError, isLoading : hintsLoading } = useTeamHintRedemptions(eventId, teamId);
  const { data : manualAwards, error : manualAwardsError, isLoading : manualAwardsLoading } = useTeamManualAwards(eventId, teamId);

  // memoize merging the arrays, sorting by timestamp (descending)
  const merged = useMemo(
    () => [ ...(attempts ?? []), ...(hintRedemptions ?? []), ...(manualAwards ?? []) ]
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime()),
    [ attempts, hintRedemptions, manualAwards ],
  );

  return (
    <>
      {attemptsError && <ErrorCallout>{attemptsError.message}</ErrorCallout>}
      {hintsError && <ErrorCallout>{hintsError.message}</ErrorCallout>}
      {manualAwardsError && <ErrorCallout>{manualAwardsError.message}</ErrorCallout>}
      <AgGridReact
        columnDefs={colDefs}
        rowData={merged}
        theme={radixTheme}
        loading={attemptsLoading || hintsLoading || manualAwardsLoading}
        className="min-h-160"
      />
    </>
  );
}
