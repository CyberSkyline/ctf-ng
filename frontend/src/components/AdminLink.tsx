import { COLOR_INFO } from '@/constants';
import { utf8ToBase64 } from '@/util';
import { Button } from '@radix-ui/themes';
import type { FilterModel } from 'ag-grid-community';
import type { IconType } from 'react-icons';
import { Link } from 'react-router';

export default function AdminLink({
  to, icon : Icon, label, id, filter,
}: {to: string, icon?: IconType, label: string, id?: number, filter?: FilterModel}) {
  const params = new URLSearchParams();

  if (id !== undefined) {
    params.append('id', id.toString());
  }

  if (filter !== undefined) {
    params.append('filter', utf8ToBase64(JSON.stringify(filter)));
  }

  return (
    <Button
      variant="soft"
      color={COLOR_INFO}
      aria-label={`Navigate to associated ${label}`}
      asChild
    >
      <Link
        to={params.toString() ? `${to}?${params.toString()}` : to}
      >
        {Icon && <Icon />}
        {label}
      </Link>
    </Button>
  );
}
