import type { Challenge } from '@/types';
import {
  Card,
  Flex,
  Heading,
  Text,
} from '@radix-ui/themes';
import ChallengeIcon from 'components/ChallengeIcon';
import { Link } from 'react-router';

export default function AdminChallengeCard({ challenge }: { challenge: Challenge }) {
  return (
    <Card asChild>
      <Link to={`/admin/challenges?id=${challenge.id}`}>
        <Flex direction="row" align="center" gap="1">
          <ChallengeIcon icon={challenge.icon} />
          <Heading size="3">
            {challenge.name}
          </Heading>
        </Flex>
        <Text color="gray">
          {challenge.summary}
        </Text>
      </Link>
    </Card>
  );
}
