import { ROLES } from '@/constants';
import { Badge } from '@radix-ui/themes';

export default function RoleBadge({ value }: { value: string }) {
  const color = ROLES[value]?.color || 'gray';
  const Icon = ROLES[value]?.icon;

  if (!value) {
    return null;
  }

  return (
    <Badge color={color} variant="soft">
      {Icon && <Icon />}
      {' '}
      {value.charAt(0).toUpperCase() + value.slice(1)}
    </Badge>
  );
}
