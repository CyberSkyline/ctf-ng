import { ROLES } from '@/constants';
import { Badge } from '@radix-ui/themes';
import type { Responsive } from '@radix-ui/themes/props';

export default function RoleBadge({ value, size = '1' }: { value: string, size?: Responsive<'1' | '2' | '3'> }) {
  const color = ROLES[value]?.color || 'gray';
  const Icon = ROLES[value]?.icon;

  if (!value) {
    return null;
  }

  return (
    <Badge color={color} variant="soft" size={size}>
      {Icon && <Icon />}
      {' '}
      {value.charAt(0).toUpperCase() + value.slice(1)}
    </Badge>
  );
}
