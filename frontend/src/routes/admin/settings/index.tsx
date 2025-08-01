import {
  Box,
  Container,
  Flex,
  Heading,
} from '@radix-ui/themes';
import { InfoCallout } from 'components/Callouts';

/**
 * Global application configuration forms for admins.
 */
export default function AdminSettings() {
  return (
    <Container size="4">
      <Flex direction="column" gap="4">
        <Box>
          <Heading>Section</Heading>
          <InfoCallout>
            Config form.
          </InfoCallout>
        </Box>
        <Box>
          <Heading>Section</Heading>
          <InfoCallout>
            Config form.
          </InfoCallout>
        </Box>
        <Box>
          <Heading>Section</Heading>
          <InfoCallout>
            Config form.
          </InfoCallout>
        </Box>
      </Flex>
    </Container>
  );
}
