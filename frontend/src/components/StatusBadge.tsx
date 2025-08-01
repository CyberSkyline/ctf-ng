import { COLOR_INFO, COLOR_POSITIVE, COLOR_WARNING } from '@/constants';
import { Badge } from '@radix-ui/themes';
import type { ICellRendererParams } from 'ag-grid-community';

const CLOSED = 'closed';
const IN_PROGRESS = 'inprogress';

function StatusBadge(status: string) {
  switch (status) {
    case CLOSED: return <Badge color={COLOR_POSITIVE}>Closed</Badge>;
    case IN_PROGRESS: return <Badge color={COLOR_INFO}>In Progress</Badge>;
    default: return <Badge color={COLOR_WARNING}>Open</Badge>;
  }
}

function StatusBadgeCell({ value }: ICellRendererParams) {
  switch (value) {
    case CLOSED: return <Badge color={COLOR_POSITIVE}>Closed</Badge>;
    case IN_PROGRESS: return <Badge color={COLOR_INFO}>In Progress</Badge>;
    default: return <Badge color={COLOR_WARNING}>Open</Badge>;
  }
}

export {
  StatusBadge,
  StatusBadgeCell,
};
