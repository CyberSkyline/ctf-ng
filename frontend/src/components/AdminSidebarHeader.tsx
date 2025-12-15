import { Flex, Heading } from '@radix-ui/themes';

export default function AdminSidebarHeader({
  title,
  icon,
  children,
  id,
} : {
  title: string;
  icon?: React.ReactNode;
  children?: React.ReactNode
  id?: string;
}) {
  return (
    <Flex direction="row" align="center" justify="between" gap="2">
      <Flex direction="row" align="center" gap="2">
        {icon && <Heading aria-hidden>{icon}</Heading>}
        <Heading id={id}>{title}</Heading>
      </Flex>
      <Flex direction="row" align="center" gap="2" wrap="wrap" justify="end">
        {children}
      </Flex>
    </Flex>
  );
}
