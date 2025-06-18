import Statistic from '@/components/Statistic';
import { Card, Flex } from '@radix-ui/themes';

export default function AdminOverviewCard() {
  return (
    <Card>
      <Flex gap="4">
        <Statistic label="Active Users" value={123} delta="+10%" description="Number of active user sessions." />
        <Statistic label="Something" value={456} delta="-10%" description="Number of something." />
        <Statistic label="Errors" value={0} />
      </Flex>
    </Card>
  );
}
