import { useCounts } from '@/hooks/stats';
import { Card, Flex, Heading } from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import Statistic from 'components/Statistic';

export default function AdminCountsCard() {
  const { data, error } = useCounts();

  if (error) {
    return (
      <ErrorCallout>
        Failed to load totals.
        <br />
        {error.message}
      </ErrorCallout>
    );
  }

  return (
    <Card>
      <Heading>Totals</Heading>
      <Flex gap="4" mt="3">
        <Statistic
          label="Events"
          value={data?.events || ''}
        />
        <Statistic
          label="Users"
          value={data?.users || ''}
        />
        <Statistic
          label="Teams"
          value={data?.teams || ''}
        />
      </Flex>
    </Card>
  );
}
