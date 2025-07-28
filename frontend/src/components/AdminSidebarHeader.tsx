import { Flex, Heading } from '@radix-ui/themes';

export default function AdminSidebarHeader({
  title,
  children,
} : {
  title: string;
  children?: React.ReactNode
}) {
  return (
    <Flex direction="row" align="center" justify="between" gap="4">
      <Heading>{title}</Heading>
      <Flex direction="row" align="center" gap="2">
        {children}
      </Flex>
    </Flex>
  );
}
