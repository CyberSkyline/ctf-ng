import {
  Container,
  Flex,
  Heading,
  Link as RadixLink,
  Text,
} from '@radix-ui/themes';
import { Link } from 'react-router';
import Accordion from 'components/Accordion';
import AdminFaqs from './AdminFaqs';

export default function FAQPage() {
  return (
    <Container size="4">
      <Flex gap="3" direction="column">
        <Heading>FAQs</Heading>
        <Accordion.Root
          type="multiple"
        >
          <Accordion.Item value="0">
            <Accordion.Header>
              <Accordion.Trigger>
                How do I log in?
              </Accordion.Trigger>
            </Accordion.Header>
            <Accordion.Content>
              <Text as="p">
                Go to the
                {' '}
                <RadixLink asChild><Link to="/login">login page</Link></RadixLink>
                {`
                and acknowledge the
                notice and competition rules. Log in with your SSO credentials. If you have been
                given an expo account login, please click the "use an expo account" option to log in.
                `}
              </Text>
              <Text as="p">
                For instructions on how to create an account, please visit
                {' '}
                <RadixLink href="https://presidentscup.cisa.gov/pc8/#registration">
                  {`President's Cup Website`}
                </RadixLink>
                {' '}
                for details.
              </Text>
            </Accordion.Content>
          </Accordion.Item>

          <Accordion.Item value="1">
            <Accordion.Header>
              <Accordion.Trigger>
                How do I register for an event?
              </Accordion.Trigger>
            </Accordion.Header>
            <Accordion.Content>
              <Text as="p">
                To register for an event, first
                {' '}
                <RadixLink asChild><Link to="/login">log in</Link></RadixLink>
                {' '}
                to the platform.
              </Text>
              <Text as="p">
                You must have a sponsor set on your
                {' '}
                <RadixLink asChild><Link to="/profile?sponsor=1">profile page</Link></RadixLink>
                {' '}
                prior to registering for an event.
              </Text>
              <Text as="p">
                {`
                Navigate to the event you wish to register for and click the "Register" button. 
                If you are participating in a team event, you can create your own team or use an invite code provided from the team captain to join their team.
              `}
              </Text>
            </Accordion.Content>
          </Accordion.Item>

          <Accordion.Item value="2">
            <Accordion.Header>
              <Accordion.Trigger>
                How do I join a team?
              </Accordion.Trigger>
            </Accordion.Header>
            <Accordion.Content>
              <Text as="p">
                {`
                To join an existing team, you need to request an invite code from the team's captain.
                Follow the invite code link in the browser, or manually input the code during event registration by clicking on the "Join Existing Team" option.
              `}
              </Text>
              <Text as="p">
                {`
                To create a new team, click on the event registration button and select the "Create New Team" option.
                You will automatically be the team captain of the team.
              `}
              </Text>
            </Accordion.Content>
          </Accordion.Item>

          <Accordion.Item value="3">
            <Accordion.Header>
              <Accordion.Trigger>
                How do I reset my Kali workspace?
              </Accordion.Trigger>
            </Accordion.Header>
            <Accordion.Content>
              <Text as="p">
                If your Kali workspace becomes unresponsive, go to the
                <RadixLink asChild><Link to="/profile">profile page</Link></RadixLink>
                {' '}
                and use the Workspace - Restart option.
              </Text>
              <Text as="p">
                If restarting the workspace does not resolve the issue, you may need to
                {' '}
                <RadixLink asChild><Link to="/support/createTicket">contact support</Link></RadixLink>
                {' '}
                for further assistance.
              </Text>
            </Accordion.Content>
          </Accordion.Item>

          <Accordion.Item value="4">
            <Accordion.Header>
              <Accordion.Trigger>
                How do I get my certificate of completion?
              </Accordion.Trigger>
            </Accordion.Header>
            <Accordion.Content>
              <Heading>Practice Area:</Heading>
              <Text as="p">
                Certificates are available on the challenge page after all questions in a challenge are answered correctly.
              </Text>
              <Heading className="pt-2">Events:</Heading>
              <Text as="p">
                {`
                Certificates are available on the event's page after the event has ended.
              `}
              </Text>
            </Accordion.Content>
          </Accordion.Item>
        </Accordion.Root>

        <AdminFaqs />
      </Flex>
    </Container>
  );
}
