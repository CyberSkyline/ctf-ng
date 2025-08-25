import { COLOR_POSITIVE, COLOR_WARNING } from '@/constants';
import { Badge } from '@radix-ui/themes';
import type { ICellRendererParams } from 'ag-grid-community';

const CLOSED = 'closed';

function StatusBadge(status: string) {
  switch (status) {
    case CLOSED: return <Badge color={COLOR_POSITIVE}>Closed</Badge>;
    default: return <Badge color={COLOR_WARNING}>Open</Badge>;
  }
}

function StatusBadgeCell({ value }: ICellRendererParams) {
  switch (value) {
    case CLOSED: return <Badge color={COLOR_POSITIVE}>Closed</Badge>;
    default: return <Badge color={COLOR_WARNING}>Open</Badge>;
  }
}

export {
  StatusBadge,
  StatusBadgeCell,
};
