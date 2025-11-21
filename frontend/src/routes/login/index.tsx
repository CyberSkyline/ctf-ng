import { SSOPATH } from '@/constants';
import {
  Box,
  Button,
  Card,
  Flex,
  Heading,
  Link as RadixLink,
  Text,
} from '@radix-ui/themes';
import { useState } from 'react';
import { Link } from 'react-router';
import ExpoLoginForm from './ExpoLoginForm';
import GovernmentNotice from './GovernmentNotice';

export default function Login() {
  const [ hasAcceptedNotice, setHasAcceptedNotice ] = useState(false);

  const handleAcceptNotice = () => {
    setHasAcceptedNotice(true);
  };

  if (!hasAcceptedNotice) {
    return <GovernmentNotice onAccept={handleAcceptNotice} />;
  }

  return (
    <Flex className="absolute inset-0 overflow-hidden bg-dots-1" align="center" justify="center" direction="column" gap="3" p="3">
      <title>Login</title>
      <Card size="3">
        <Flex direction="column" className="max-w-96" gap="3" align="center">
          <Heading size="8">Log in</Heading>
          <Text color="gray">
            To continue, please log in with your organization&apos;s Single Sign-On (SSO) provider.
          </Text>

          <Button asChild size="4" className="!w-full">
            <Link to={SSOPATH} reloadDocument>
              Log in with SSO
            </Link>
          </Button>

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
