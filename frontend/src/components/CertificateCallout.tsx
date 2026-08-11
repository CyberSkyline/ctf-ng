import { COLOR_INFO } from '@/constants';
import { useMyChallenges } from '@/hooks/challenge';
import { useEvent, useEventStatus } from '@/hooks/events';
import { useRegistration } from '@/hooks/users';
import {
  Button,
  Callout,
  Flex,
  Heading,
  Text,
} from '@radix-ui/themes';
import { TbCertificate, TbDownload } from 'react-icons/tb';
import { Link } from 'react-router';

export default function CertificateCallout({
  eventId,
  challengeId,
}: {
  eventId: number,
  challengeId?: number,
}) {
  const { data : event } = useEvent(eventId);
  const { isConcluded } = useEventStatus(eventId);
  const { isStarted, isFinished } = useRegistration(eventId);
  // per-challenge completion only matters for the practice certificate
  const { data : myChallenges } = useMyChallenges(
    challengeId !== undefined && event?.practice ? eventId : null,
  );

  if (!event?.has_certificate) {
    return null;
  }

  let href: string | null = null;
  if (challengeId !== undefined) {
    // challenge page: challenge must be complete
    if (event.practice) {
      const progress = myChallenges?.find((c) => c.challenge_id === challengeId);
      if (progress?.is_completed) {
        href = `/ng/events/${eventId}/challenges/${challengeId}/certificate`;
      }
    }
  } else if (!event.practice && isStarted && isFinished && (!event.end_time || isConcluded)) {
    // event page: team must be finished, event must be concluded if it has an end time
    href = `/ng/events/${eventId}/certificate`;
  }

  if (!href) {
    return null;
  }

  href += `?tz=${encodeURIComponent(Intl.DateTimeFormat().resolvedOptions().timeZone)}`;

  return (
    <Callout.Root variant="surface" color={COLOR_INFO}>
      <Callout.Icon>
        <TbCertificate />
      </Callout.Icon>
      <Flex direction="column" align="start">
        <Heading size="2">Certificate of Completion</Heading>
        <Text size="2">Recognize your achievement with an official certificate of completion.</Text>
        <Button variant="soft" size="1" mt="3" asChild>
          <Link to={href} target="_blank" rel="noopener noreferrer">
            <TbDownload />
            Download
          </Link>
        </Button>
      </Flex>
    </Callout.Root>
  );
}
