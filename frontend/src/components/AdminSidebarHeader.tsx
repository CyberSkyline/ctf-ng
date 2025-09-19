import { Flex, Heading } from '@radix-ui/themes';

export default function AdminSidebarHeader({
  title,
  icon,
  children,
} : {
  title: string;
  icon?: React.ReactNode;
  children?: React.ReactNode
}) {
  return (
    <Flex direction="row" align="center" justify="between" gap="2">
      <Flex direction="row" align="center" gap="2">
        {icon && <Heading>{icon}</Heading>}
        <Heading>{title}</Heading>
      </Flex>
      <Flex direction="row" align="center" gap="2">
        {children}
      </Flex>
    </Flex>
  );
}
