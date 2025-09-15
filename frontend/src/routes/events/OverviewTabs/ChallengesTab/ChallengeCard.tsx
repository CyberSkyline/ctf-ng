import { COLOR_POSITIVE, COLOR_WARNING, type AccentColor } from '@/constants';
import type { Challenge, MeChallenge } from '@/types';
import {
  Box,
  Card,
  Flex,
  Heading,
  Skeleton,
  Text,
} from '@radix-ui/themes';
import ChallengeIcon from 'components/ChallengeIcon';
import * as tb from 'react-icons/tb';
import { Link } from 'react-router';

function getPercentageIcon(progress: number) {
  let percentage: number;
  if (progress <= 0) {
    percentage = 0;
  } else if (Math.abs(progress - 0.25) < 0.02) {
    percentage = 25;
  } else if (Math.abs(progress - 0.33) < 0.02) {
    percentage = 33;
  } else if (Math.abs(progress - 0.66) < 0.02) {
    percentage = 66;
  } else if (Math.abs(progress - 0.75) < 0.02) {
    percentage = 75;
  } else if (progress >= 1) {
    percentage = 100;
  } else {
    // don't allow rounding to an empty or full circle - clamp between 10 and 90
    percentage = Math.min(90, Math.max(10, Math.round(progress * 10) * 10));
  }

  const iconName = `TbPercentage${percentage}`;
  const Icon = tb[iconName as keyof typeof tb] || tb.TbPercentage0;
  return <Icon />;
}

export default function ChallengeCard({
  challenge,
  progress,
}: {
  challenge: Challenge,
  progress: MeChallenge | undefined,
}) {
  const complete = progress && progress.num_questions_solved === progress.num_questions_available;
  const inProgress = progress && progress.num_attempts_made > 0 && !complete;

  let color: AccentColor | undefined;

  if (complete) {
    color = COLOR_POSITIVE;
  } else if (inProgress) {
    color = COLOR_WARNING;
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
              {getPercentageIcon(progress.num_questions_solved / progress.num_questions_available)}
            </Text>
          )}
          <Skeleton loading={!progress}>
            <Text size="2" color={color}>
              {progress?.total_points_scored ?? '000'}
              /
              {progress?.total_points_available ?? '000'}
            </Text>
          </Skeleton>
        </Flex>
        <Text color="gray">{challenge.summary}</Text>
      </Link>
    </Card>
  );
}
