import {
  ChallengeIcon,
  EventIcon,
  TeamIcon,
  UserIcon,
} from '@/constants';
import type { AdminTicket } from '@/types';
import type { ColDef, ICellRendererParams } from 'ag-grid-community';
import AdminGrid from 'components/AdminGrid';
import Entity from 'components/Entity';
import { StatusBadgeCell } from 'components/StatusBadge';
import type { IconType } from 'react-icons';
import MessagesSidebar from './MessagesSidebar';

function NameLinkCell(
  {
    name,
    id,
    linkTo,
    icon,
  }: {
    name?: string,
    id?: number,
    linkTo: string,
    icon: IconType
  },
) {
  if (id == null || name == null) return null;

  return (
    <Entity
      to={linkTo}
      label={name}
      icon={icon}
    />
  );
}

// specify types explicitly since there's no rowData to infer from
const colDefs: ColDef<AdminTicket>[] = [
  {
    field : 'status',
    headerName : 'Status',
    cellDataType : 'text',
    cellRenderer : (params: ICellRendererParams<AdminTicket>) => params.data && StatusBadgeCell(params),
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'subject',
    headerName : 'Subject',
    cellDataType : 'text',
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'author_name',
    headerName : 'Author',
    cellDataType : 'text',
    cellRenderer : (params: ICellRendererParams<AdminTicket>) => params.data && (
      <NameLinkCell
        id={params.data.author_id}
        name={params.data.author_name}
        linkTo={`/admin/users?id=${params.data.author_id}`}
        icon={UserIcon}
      />
    ),
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'last_updated',
    headerName : 'Updated Date',
    cellDataType : 'dateString',
    filter : 'agDateColumnFilter',
    floatingFilter : true,
    sort : 'desc',
  },
  {
    field : 'event_name',
    headerName : 'Event',
    cellDataType : 'text',
    cellRenderer : (params: ICellRendererParams<AdminTicket>) => params.data && (
      <NameLinkCell
        id={params.data.event_id}
        name={params.data.event_name}
        linkTo={`/admin/events?id=${params.data.event_id}`}
        icon={EventIcon}
      />
    ),
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'team_name',
    headerName : 'Team',
    cellDataType : 'text',
    cellRenderer : (params: ICellRendererParams<AdminTicket>) => params.data && (
      <NameLinkCell
        id={params.data.team_id}
        name={params.data.team_name}
        linkTo={`/admin/teams?id=${params.data.team_id}`}
        icon={TeamIcon}
      />
    ),
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'challenge_name',
    headerName : 'Challenge',
    cellDataType : 'text',
    cellRenderer : (params: ICellRendererParams<AdminTicket>) => params.data && (
      <NameLinkCell
        id={params.data.challenge_id}
        name={params.data.challenge_name}
        linkTo={`/admin/challenges?id=${params.data.challenge_id}`}
        icon={ChallengeIcon}
      />
    ),
    filter : true,
    floatingFilter : true,
  },
  {
    field : 'opened_timestamp',
    headerName : 'Created Date',
    cellDataType : 'dateString',
    filter : 'agDateColumnFilter',
    floatingFilter : true,
  },
];

export default function AdminTickets() {
  return (
    <>
      <title>Admin Tickets</title>
      <AdminGrid
        collectionKey="/admin/support/tickets"
        columnDefs={colDefs}
        getRowId={(params) => params.data.id.toString()}
        sidebarComponent={MessagesSidebar}
        stopCellSelection={[
          'author_name',
          'event_name',
          'team_name',
          'challenge_name',
        ]}
      />
    </>
  );
}
