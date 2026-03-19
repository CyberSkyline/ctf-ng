import {
  Button,
  Card,
  Flex,
  Heading,
  Link as RadixLink,
  Text,
} from '@radix-ui/themes';

import { WELCOME_PAGE } from '@/constants';
import { TbArrowRight, TbUserCircle } from 'react-icons/tb';
import { Link } from 'react-router';

export default function Landing() {
  return (
    <Flex className="absolute inset-0 overflow-hidden bg-dots-1" align="center" justify="center" direction="column" gap="3" p="3">
      <title>Home</title>
      <Heading size="8">{`Welcome to ${WELCOME_PAGE.NAME}`}</Heading>
      <Card size="3" className="max-w-172" role="main">
        <Flex direction="row" gap="8">
          <Flex direction="column" gap="2" flexGrow="1" flexBasis="0">
            <Text color="gray">
              To register and participate, you must log in. You may also view event details and standings without logging in.
            </Text>
            <Text color="gray">
              See
              {' '}
              <RadixLink href={`https://${WELCOME_PAGE.LINK}`}>{WELCOME_PAGE.LINK}</RadixLink>
              {' '}
              {`for more information about the ${WELCOME_PAGE.NAME} Cybersecurity Competition.`}
            </Text>
          </Flex>
          <Flex direction="column" gap="2" flexGrow="1" flexBasis="0">
            <Button asChild size="4">
              <Link to="/login">
                Log In
                <TbUserCircle />
              </Link>
            </Button>
            <Button variant="soft" size="3" asChild>
              <Link to="/events">
                View Events
                <TbArrowRight />
              </Link>
            </Button>
          </Flex>
        </Flex>
      </Card>
    </Flex>
  );
}
