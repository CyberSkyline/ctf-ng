import { Flex, Heading, Skeleton } from '@radix-ui/themes';

export default function AdminSidebarHeader({
  title,
  icon,
  children,
  id,
  loading = false,
} : {
  title: string;
  icon?: React.ReactNode;
  children?: React.ReactNode
  id?: string;
  loading?: boolean;
}) {
  return (
    <Flex direction="row" align="center" justify="between" gap="2">
      <Flex direction="row" align="center" gap="2">
        {icon && <Heading aria-hidden>{icon}</Heading>}
        <Skeleton loading={loading}>
          <Heading id={id} className="wrap-anywhere">{title}</Heading>
        </Skeleton>
      </Flex>
      <Skeleton loading={loading}>
        <Flex direction="row" align="center" gap="2" wrap="wrap" justify="end">
          {children}
        </Flex>
      </Skeleton>
    </Flex>
  );
}
