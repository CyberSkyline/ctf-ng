import { usePracticeEvents } from '@/hooks/events';
import {
  Button,
  Card,
  Container,
  Flex,
  Heading,
} from '@radix-ui/themes';
import RadixMarkdown from 'components/RadixMarkdown';
import { TbExternalLink } from 'react-icons/tb';
import { Link } from 'react-router';

export default function Practice() {
  const { data } = usePracticeEvents();
  const practiceEvent = data?.[0];
  const practiceBtnText = 'Go to PC7 Practice Area';

  return (
    <Container size="2" align="center" className="mt-12">
      <title>Practice</title>
      <Card size="4" className="max-w-2xl">
        <Flex direction="column" gap="4">
          <Heading size="6" align="center">Notice</Heading>
          <Flex
            direction="column"
            gap="4"
            align="center"
            flexGrow="1"
            overflowY="auto"
            px="4"
            className="max-h-[50vh]"
          >
            <RadixMarkdown>
              {`
The Practice Area hosts President's Cup challenges from past competitions and is open to all. Participants can earn certificates of completion for
 each challenge, which may be used for PDU/CPE credits.

**Please note that the legacy Practice Area will be decommissioned on May 22, 2026.**
Our team is working to convert and transfer these challenges onto this platform.

If you have any information or resources in the legacy Practice Area that you wish to keep, please be sure to download or save them prior to May 22, 2026.
After this date, the legacy platform will no longer be accessible.

For additional resources, visit the [prescup-challenges GitHub](https://github.com/cisagov/prescup-challenges) for solution guides,
 challenge code, virtual machine builds, and containers.

*For questions about access or eligibility, please [contact the President's Cup team](mailto:presidentscup@cisa.dhs.gov).*
              `}
            </RadixMarkdown>
          </Flex>
          <Flex justify="between" className="border-t border-[var(--gray-7)]" pt="4">
            <Button disabled={!practiceEvent}>
              {practiceEvent
                ? <Link to={`/events/${practiceEvent.id}`}>{practiceBtnText}</Link>
                : practiceBtnText}
            </Button>
            <Button>
              <a href="https://pccc.cisa.gov/gb">Go to Legacy Practice Area</a>
              <TbExternalLink />
            </Button>
          </Flex>
        </Flex>
      </Card>
    </Container>
  );
}
