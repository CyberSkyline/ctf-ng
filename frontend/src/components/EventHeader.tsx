import {
  Heading, Text, Flex, Box, AspectRatio,
} from '@radix-ui/themes';
import EventBadge from './EventBadge';

export default function EventHeader({
  name,
  description,
  state,
  children = undefined,
}: {
    name: string;
    description: string;
    state: 'upcoming' | 'waiting' | 'live' | 'ended';
    children?: React.ReactNode;
}) {
  return (
    <Flex direction="row" gap="6" align="start">
      <Box className="w-32" flexShrink="0">
        <AspectRatio ratio={3 / 4}>
          {/* Placeholder for event card image */}
          <Box className="h-full w-full bg-[var(--lime-8)] rounded-lg shadow-xl" />
        </AspectRatio>
      </Box>
      <Flex direction="column" flexGrow="1" align="start" gap="2">
        {state && (
          <EventBadge state={state} />
        )}
        <Box>
          <Heading size="9">{name}</Heading>
          <Text as="p" color="gray">{description}</Text>
        </Box>
        {children}
      </Flex>
    </Flex>
  );
}
