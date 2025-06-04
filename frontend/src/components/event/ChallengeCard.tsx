import {
  Box, Card, Flex, Heading, Text,
} from '@radix-ui/themes';
import type { IconType } from 'react-icons';
import {
  FaCheck,
} from 'react-icons/fa6';
import { Link } from 'react-router';

export default function ChallengeCard({
  id,
  name,
  description,
  points,
  completed = false,
  icon: Icon = undefined,
}: {
    id: string;
    name: string;
    description: string;
    points: number;
    completed?: boolean;
    icon?: IconType;
}) {
  return (
    <Card asChild>
      <Link to={`./challenge/${id}`}>
        <Flex direction="row" align="center" gap="1">
          {Icon ? (
            <Heading size="4" color="lime">
              <Icon />
            </Heading>
          ) : null}
          <Heading size="4" color="lime">{name}</Heading>
          <Box flexGrow="1" />
          {completed ? (
            <Text size="2" color="lime">
              <FaCheck title="Completed" />
            </Text>
          ) : null}
          <Text size="2" color={completed ? 'lime' : 'gray'} aria-label={`${points} points`}>
            {points}
            pts
          </Text>
        </Flex>
        <Text>{description}</Text>
      </Link>
    </Card>
  );
}
