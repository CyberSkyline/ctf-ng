import { Flex, Link as RadixLink } from '@radix-ui/themes';
import type { IconType } from 'react-icons';
import { Link } from 'react-router';

/**
 * Link to an entity (e.g., user, team, event) with an icon and label.
 */
export default function Entity({
  label,
  to,
  icon : Icon,
}: {
    label: string;
    to: string;
    icon: IconType;
}) {
  return (
    <RadixLink asChild>
      <Link to={to}>
        <Flex direction="row" align="center" gap="1" className="h-full">
          <Icon className="shrink-0" />
          <span>{label}</span>
        </Flex>
      </Link>
    </RadixLink>
  );
}
