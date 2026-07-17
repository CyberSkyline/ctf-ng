import { COLOR_POSITIVE, COLOR_WARNING } from '@/constants';
import { Badge } from '@radix-ui/themes';
import type { ICellRendererParams } from 'ag-grid-community';
import type { ComponentProps } from 'react';

const CLOSED = 'closed';

function StatusBadge({ status, size = '1' } : {status: string, size?: ComponentProps<typeof Badge>['size']}) {
  switch (status) {
    case CLOSED: return <Badge color={COLOR_POSITIVE} size={size}>Closed</Badge>;
    default: return <Badge color={COLOR_WARNING} size={size}>Open</Badge>;
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
