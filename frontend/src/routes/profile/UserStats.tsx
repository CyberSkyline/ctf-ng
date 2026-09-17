import { useCurrentUser, useMyStats } from '@/hooks/users';
import { formatDate } from '@/util';
import {
  Box,
  Flex,
  Heading,
  Skeleton,
  Text,
} from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import Statistic from 'components/Statistic';

export default function UserStats() {
  const { data : currentUser, isLoading : userLoading } = useCurrentUser();
  const { data : stats, error, isLoading : statsLoading } = useMyStats();

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  return (
    <Flex direction="column" gap="4">
      <Box>
        <Heading as="h2">Statistics</Heading>
        <Text color="gray" trim="end">A summary of your activity.</Text>
      </Box>
      <Skeleton loading={userLoading || statsLoading}>
        <Flex gap="6" wrap="wrap" justify="between">
          <Statistic
            label="Member Since"
            value={formatDate(currentUser?.registered_at, { year : 'numeric', month : 'numeric', day : 'numeric' }) || 'Loading'}
          />
          <Statistic
            label="Events Played"
            value={stats?.events_participated ?? 'Loading'}
            description="Number of events you have played in."
          />
          <Statistic
            label="Correct Answers"
            value={stats?.total_correct_submissions ?? 'Loading'}
            description="Total number of questions you have answered correctly."
          />
          <Statistic
            label="Practice Solves"
            value={stats?.practice_challenges_completed ?? 'Loading'}
            description="Number of practice challenges you have fully solved."
          />
        </Flex>
      </Skeleton>
    </Flex>
  );
}
