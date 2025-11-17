import { useEvent, useEventStatus } from '@/hooks/events';
import {
  Box,
  Container,
  Flex,
  Heading,
  Text,
} from '@radix-ui/themes';
import { TbCancel } from 'react-icons/tb';
import { useParams } from 'react-router';

export default function NotAvailable() {
  const { idEvent } = useParams();
  const { data : event } = useEvent(Number(idEvent));
  const { isOngoing, isConcluded } = useEventStatus(Number(idEvent));

  return (
    <Container size="2" className="text-center">
      <Flex direction="column" gap="2" align="center">
        <TbCancel className="inline text-9xl my-8" />
        <Box>
          <Heading size="5">
            Challenges are not available at this time.
          </Heading>
          {!isOngoing && !isConcluded && event?.start_time && (
            <Text size="3" color="gray">
              The event will start on
              {' '}
              {event.start_time.toLocaleDateString()}
              {' at '}
              {event.start_time.toLocaleTimeString()}
              .
            </Text>
          )}
          {isConcluded && (
            <Text size="3" color="gray">
              This event has concluded.
            </Text>
          )}
        </Box>
      </Flex>
    </Container>
  );
}
