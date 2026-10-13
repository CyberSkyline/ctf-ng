import { SSO_LOGIN_PATH, SSO_REGISTRATION_PATH } from '@/constants';
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
import { Link, useSearchParams } from 'react-router';
import { savePostLoginRedirect } from '@/postLoginRedirect';
import ExpoLoginForm from './ExpoLoginForm';
import GovernmentNotice from './GovernmentNotice';

export default function Login() {
  const [ hasAcceptedNotice, setHasAcceptedNotice ] = useState<boolean>(false);
  const [ searchParams ] = useSearchParams();

  return (
    <Flex
      className="min-h-[calc(100vh-var(--NavBarHeight)-var(--FooterBarHeight))] -m-3 inset-0 overflow-hidden bg-dots-1"
      align="center"
      justify="center"
      direction="column"
      gap="3"
      p="3"
    >
      <title>Login</title>
      {hasAcceptedNotice ? (
        <Card size="3">
          <Flex direction="column" className="max-w-96" gap="3" align="center">
            <Heading size="8">Log in</Heading>
            <Text color="gray">
              To continue, please log in with your organization&apos;s Single Sign-On (SSO) provider.
            </Text>

            <Button asChild size="4" className="!w-full">
              <Link
                to={SSO_LOGIN_PATH}
                reloadDocument
                // the SSO round trip drops the redirect param, so remember it until we're back
                onClick={() => savePostLoginRedirect(searchParams.get('redirect'))}
              >
                Log in with SSO
              </Link>
            </Button>

            <Button asChild size="4" variant="soft" className="!w-full">
              <Link to={SSO_REGISTRATION_PATH} reloadDocument>
                Create SSO Account
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
      ) : <GovernmentNotice onAccept={() => setHasAcceptedNotice(true)} />}
    </Flex>
  );
}
