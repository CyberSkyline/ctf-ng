import { Badge } from '@radix-ui/themes';
import type { ICellRendererParams } from 'ag-grid-community';

const CLOSED = 'closed';
const IN_PROGRESS = 'inprogress';

function StatusBadge(status: string) {
  switch (status) {
    case CLOSED: return <Badge color="jade">Closed</Badge>;
    case IN_PROGRESS: return <Badge color="blue">In Progress</Badge>;
    default: return <Badge color="orange">Open</Badge>;
  }
}

function StatusBadgeCell({ value }: ICellRendererParams) {
  switch (value) {
    case CLOSED: return <Badge color="jade">Closed</Badge>;
    case IN_PROGRESS: return <Badge color="blue">In Progress</Badge>;
    default: return <Badge color="orange">Open</Badge>;
  }
}

export {
  StatusBadge,
  StatusBadgeCell,
};
