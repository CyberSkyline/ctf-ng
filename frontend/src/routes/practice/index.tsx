import {
  Button,
  Card,
  Container,
  Flex,
  Heading,
} from '@radix-ui/themes';
import RadixMarkdown from 'components/RadixMarkdown';
import { TbExternalLink } from 'react-icons/tb';

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
The Practice Area is a repository of President's Cup challenges from past competitions, open to federal employees and active duty military and reservist
 service members only. Users can receive a certificate of completion after each challenge (may be used for PDU/CPEs).

**The Practice Area is hosted on the old competition platform and uses your original account credentials (not connected to Login.gov).** If you have not 
visited the Practice Area in previous competitions, please follow the registration prompts provided to create a login.

The President's Cup team is actively working to migrate challenges from the old platform to the new one and will provide updates appropriately.

The [prescup-challenges GitHub](https://github.com/cisagov/prescup-challenges) project has practice resources available including solution guides, challenge 
code from all previous competitions, virtual machine builds, and challenge containers.

*Not a federal, military, or active duty reservist? [Contact](mailto:presidentscup@cisa.dhs.gov) the President's Cup team to access past challenges on 
our Expo Site.*
              `}
            </RadixMarkdown>
          </Flex>
          <Button>
            <a href="https://pccc.cisa.gov/gb">Go to External Practice Area</a>
            <TbExternalLink />
          </Button>
        </Flex>
      </Card>
    </Container>
  );
}
