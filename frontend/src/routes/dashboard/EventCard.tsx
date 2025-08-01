import type { Event } from '@/types';
import {
  AspectRatio,
  Box,
  Card,
  Flex,
  Heading,
  Inset,
  Text,
} from '@radix-ui/themes';
import { Link } from 'react-router';

export default function EventCard({ event }: { event: Event }) {
  return (
    <Card asChild>
      <Link to={`/events/${event.id}`}>
        <Flex direction="row" gap="4">
          <Inset side="left" className="w-32 shrink-0">
            <AspectRatio ratio={2 / 3}>
              {/* Placeholder for event card graphic */}
              <Box className="h-full w-full bg-(--accent-8)" />
            </AspectRatio>
          </Inset>
          <Flex direction="column" gap="2" className="flex-grow" justify="between">
            <Box>
              <Heading size="4">{event.name}</Heading>
              <Text size="2" color="gray">{event.description}</Text>
            </Box>
            <Box>
              <Text size="2" color="gray">
                {event.start_time?.toLocaleString()}
              </Text>
            </Box>
          </Flex>
        </Flex>
      </Link>
    </Card>
  );
}
