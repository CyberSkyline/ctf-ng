import {
  Box, Card, Flex, Heading, Text,
} from '@radix-ui/themes';
import type { IconType } from 'react-icons';
import { TbCheck } from 'react-icons/tb';
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
  const color = completed ? 'lime' : undefined;

  return (
    <Card asChild>
      <Link to={`./challenge/${id}`}>
        <Flex direction="row" align="center" gap="1">
          {Icon ? (
            <Heading size="4" color={color}>
              <Icon />
            </Heading>
          ) : null}
          <Heading size="4" color={color}>{name}</Heading>
          <Box flexGrow="1" />
          {completed ? (
            <Text size="2" color="lime">
              <TbCheck title="Completed" />
            </Text>
          ) : null}
          <Text size="2" color={color} aria-label={`${points} points`}>
            {points}
            pts
          </Text>
        </Flex>
        <Text color="gray">{description}</Text>
      </Link>
    </Card>
  );
}
