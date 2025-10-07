import {
  Box,
  Button,
  Card,
  Flex,
  Heading,
  Link as RadixLink,
  Text,
} from '@radix-ui/themes';
import ExpoLoginForm from './ExpoLoginForm';

export default function Login() {
  return (
    <Flex className="absolute inset-0 overflow-hidden bg-dots-1" align="center" justify="center" direction="column" gap="3" p="3">
      <Card size="3">
        <Flex direction="column" className="max-w-96" gap="3" align="center">
          <Heading size="8">Log in</Heading>
          <Text color="gray">
            To continue, please log in with your organization&apos;s Single Sign-On (SSO) provider.
          </Text>

          <a href="/ng/authenticate/okta/login" className="w-full">
            <Button size="4" className="!w-full">Log in with SSO</Button>
          </a>
          <Text color="gray" size="2">
            Or,
            {' '}
            <RadixLink href="#expo">use an expo account</RadixLink>
          </Text>

          <Box id="expo" className="!hidden target:!block w-full">
            <ExpoLoginForm />
          </Box>
        </Flex>
      </Card>
    </Flex>
  );
}
