import type { Challenge, MeChallenge } from '@/types';
import {
  Box,
  Card,
  Flex,
  Heading,
  Skeleton,
  Text,
} from '@radix-ui/themes';
import type { accentColors } from '@radix-ui/themes/props';
import ChallengeIcon from 'components/ChallengeIcon';
import * as tb from 'react-icons/tb';
import { Link } from 'react-router';

export default function ChallengeCard({
  challenge,
  progress,
}: {
  challenge: Challenge,
  progress: MeChallenge | undefined,
}) {
  const complete = progress && progress.num_questions_solved === progress.num_questions_available;
  const inProgress = progress && progress.num_attempts_made > 0 && !complete;

  let color: typeof accentColors[number] | undefined;

  if (complete) {
    color = 'lime';
  } else if (inProgress) {
    color = 'amber';
  }

  return (
    <Card asChild>
      <Link to={`./challenge/${challenge.id}`}>
        <Flex direction="row" align="center" gap="1">
          <Heading size="4" color={color}>
            <ChallengeIcon icon={challenge?.icon} />
          </Heading>
          <Heading size="4" color={color}>{challenge.name}</Heading>
          <Box flexGrow="1" />
          {complete && (
            <Text size="2" color={color}>
              <tb.TbCircleCheckFilled />
            </Text>
          )}
          {inProgress && (
            <Text size="2" color={color}>
              <tb.TbPercentage50 title="In Progress" />
            </Text>
          )}
          <Skeleton loading={!progress}>
            <Text size="2" color={color}>
              {progress?.total_points_scored || '000'}
              /
              {progress?.total_points_available || '000'}
            </Text>
          </Skeleton>
        </Flex>
        <Text color="gray">{challenge.summary}</Text>
      </Link>
    </Card>
  );
}
