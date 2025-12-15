import {
  Button,
  Card,
  Container,
  Flex,
  Heading,
  Text,
} from '@radix-ui/themes';
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
            <Text>
              Put verbiage here
            </Text>
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
