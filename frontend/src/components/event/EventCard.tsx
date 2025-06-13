import {
  AspectRatio,
  Box,
  Card, Flex, Heading, Inset, Text,
} from '@radix-ui/themes';
import { Link } from 'react-router';
import type { accentColors } from '@radix-ui/themes/props';
import { ROUTEPREFIX } from '../../constants';

export default function EventCard({
  id,
  name,
  description,
  color = 'lime',
}: {
  id: string;
  name: string;
  description: string;
  color?: typeof accentColors[number];
}) {
  return (
    <Card asChild>
      <Link to={`/${ROUTEPREFIX}/events/${id}`}>
        <Flex direction="row" gap="4">
          <Inset side="left" className="w-32 shrink-0">
            <AspectRatio ratio={3 / 4}>
              {/* Placeholder for event card graphic */}
              <Box className="h-full w-full" style={{ backgroundColor: `var(--${color}-8)` }} />
            </AspectRatio>
          </Inset>
          <Flex direction="column" gap="2" className="flex-grow" justify="between">
            <Box>
              <Heading size="4">{name}</Heading>
              <Text size="2" color="gray">{description}</Text>
            </Box>
            <Box>
              {/* Footer of event card text. Could include date, points, etc. */}
            </Box>
          </Flex>
        </Flex>
      </Link>
    </Card>
  );
}
