import {
  Box, Callout, Container, Flex, Heading,
} from '@radix-ui/themes';
import { TbInfoCircle } from 'react-icons/tb';

/**
 * Global application configuration forms for admins.
 */
export default function AdminSettings() {
  return (
    <Container size="4">
      <Flex direction="column" gap="4">
        <Box>
          <Heading>Section</Heading>
          <Callout.Root
            color="jade"
            variant="surface"
          >
            <Callout.Icon>
              <TbInfoCircle />
            </Callout.Icon>
            <Callout.Text>
              Config form.
            </Callout.Text>
          </Callout.Root>
        </Box>
        <Box>
          <Heading>Section</Heading>
          <Callout.Root
            color="jade"
            variant="surface"
          >
            <Callout.Icon>
              <TbInfoCircle />
            </Callout.Icon>
            <Callout.Text>
              Config form.
            </Callout.Text>
          </Callout.Root>
        </Box>
        <Box>
          <Heading>Section</Heading>
          <Callout.Root
            color="jade"
            variant="surface"
          >
            <Callout.Icon>
              <TbInfoCircle />
            </Callout.Icon>
            <Callout.Text>
              Config form.
            </Callout.Text>
          </Callout.Root>
        </Box>
      </Flex>
    </Container>
  );
}
