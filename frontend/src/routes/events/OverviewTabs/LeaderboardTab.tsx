import { Container, Flex, Skeleton } from '@radix-ui/themes';

export default function LeaderboardTab() {
  return (
    <Container size="4">
      <Flex direction="column" gap="2" py="2">
        <Skeleton height="64px" />
        <Skeleton height="64px" />
        <Skeleton height="64px" />
        <Skeleton height="64px" />
        <Skeleton height="64px" />
      </Flex>
    </Container>
  );
}
