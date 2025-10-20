import { useAdminAllTickets } from '@/hooks/support';
import type { AdminTicket } from '@/types';
import type { ColDef } from 'ag-grid-community';
import AdminGrid from 'components/AdminGrid';
import { ErrorCallout } from 'components/Callouts';
import Entity from 'components/Entity';
import { StatusBadgeCell } from 'components/StatusBadge';
import { isNull, isUndefined } from 'lodash';
import type { IconType } from 'react-icons';
import {
  ChallengeIcon,
  EventIcon,
  TeamIcon,
  UserIcon,
} from '@/constants';
import MessagesSidebar from './MessagesSidebar';

function NameLinkCell(
  {
    name,
    id,
    linkTo,
    icon,
  }: {
    name: string,
    id: number,
    linkTo: string,
    icon: IconType
  },
) {
  if (!isNull(id) && !isUndefined(name)) {
    return (
      <Entity
        to={linkTo}
        label={name}
        icon={icon}
      />
    );
  }

  return null;
}

const colDefs: ColDef<AdminTicket>[] = [
  {
    field : 'status',
    headerName : 'Status',
    cellRenderer : StatusBadgeCell,
  },
  {
    field : 'subject',
    headerName : 'Subject',
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'author_id',
    headerName : 'Author',
    cellRenderer : NameLinkCell,
    cellRendererParams : (params: { data: { author_id: number; author_name: string; }; }) => ({
      id : params.data.author_id,
      name : params.data.author_name,
      linkTo : `/admin/users?id=${params.data.author_id}`,
      icon : UserIcon,
    }),
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'last_updated',
    headerName : 'Updated Date',
    valueFormatter : (params) => params.value && params.value.toLocaleString(),
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'event_id',
    headerName : 'Event',
    cellRenderer : NameLinkCell,
    cellRendererParams : (params: { data: { event_id: number; event_name: string; }; }) => ({
      id : params.data.event_id,
      name : params.data.event_name,
      linkTo : `/admin/events?id=${params.data.event_id}`,
      icon : EventIcon,
    }),
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'team_id',
    headerName : 'Team',
    cellRenderer : NameLinkCell,
    cellRendererParams : (params: { data: { team_id: number; team_name: string; }; }) => ({
      id : params.data.team_id,
      name : params.data.team_name,
      linkTo : `/admin/teams?id=${params.data.team_id}`,
      icon : TeamIcon,
    }),
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'challenge_id',
    headerName : 'Challenge',
    cellRenderer : NameLinkCell,
    cellRendererParams : (params: { data: { challenge_id: number; challenge_name: string; event_id: number; }; }) => ({
      id : params.data.challenge_id,
      name : params.data.challenge_name,
      linkTo : `/admin/events?id=${params.data.event_id}`,
      icon : ChallengeIcon,
    }),
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'opened_timestamp',
    headerName : 'Created Date',
    valueFormatter : (params) => params.value && params.value.toLocaleString(),
    filter : true,
    floatingFilter : true,
  },
];

export default function AdminTickets() {
  const { data, error, isLoading } = useAdminAllTickets();

  return (
    <>
      <title>Admin Tickets</title>
      {error && <ErrorCallout>{error.message}</ErrorCallout>}
      <AdminGrid
        rowData={data || []}
        columnDefs={colDefs}
        loading={isLoading}
        getRowId={(params) => params.data.id.toString()}
        sidebarComponent={MessagesSidebar}
        stopCellSelection={[
          'author_id',
          'event_id',
          'team_id',
          'challenge_id',
        ]}
      />
    </>
  );
}
