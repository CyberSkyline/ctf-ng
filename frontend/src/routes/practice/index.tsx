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

**Access to PC6 and previous practice challenges is through the old competition platform using your original account credentials (not connected to 
Login.gov).** If you’re new to the Practice Area, follow the registration prompts to create a login.

We are actively migrating older challenges to the new platform, which currently hosts only PC7 challenges. Updates will be provided as more 
challenges become available.

For additional resources, visit the [prescup-challenges GitHub](https://github.com/cisagov/prescup-challenges) for solution guides,
 challenge code, virtual machine builds, and containers.

*For questions about access or eligibility, please [contact the President's Cup team](mailto:presidentscup@cisa.dhs.gov).*
              `}
            </RadixMarkdown>
          </Flex>
          <Flex justify="between" className="border-t border-[var(--gray-7)]" pt="4">
            <Button>
              <Link to="/events/7">
                Go to PC7 Practice Area
              </Link>
            </Button>
            <Button>
              <a href="https://pccc.cisa.gov/gb">Go to External Practice Area</a>
              <TbExternalLink />
            </Button>
          </Flex>
        </Flex>
      </Card>
    </Container>
  );
}
