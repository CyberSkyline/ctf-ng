import { Heading, Link as RadixLink, Text } from '@radix-ui/themes';
import { Link } from 'react-router';
import Accordion from 'components/Accordion';
import { useAuth } from '@/hooks/users';
import { useGlobalPermission } from '@/hooks/permissions';

export default function AdminFaqs() {
  const { isUnauthenticated } = useAuth();
  const { denied } = useGlobalPermission('CAN_ACCESS_ADMIN_PANEL');

  if (isUnauthenticated || denied) {
    return null;
  }

  return (
    <>
      <Heading>Admin FAQs</Heading>
      <Accordion.Root
        type="multiple"
      >
        <Accordion.Item value="a0">
          <Accordion.Header>
            <Accordion.Trigger>
              Restart vs Recycle
            </Accordion.Trigger>
          </Accordion.Header>
          <Accordion.Content>
            <Text as="p">
              On the
              {' '}
              <RadixLink asChild><Link to="/admin/deployments">Admin Deployments page</Link></RadixLink>
              , select a challenge. In the detail pane, you can modify the environment by either recycling the container or restarting it.
            </Text>
            <Text as="p">
              Restarting the container will simply stop and start the existing container. All saved data will be preserved, but unsaved work may be lost.
              This process will make the container unavailable for a short period of time.
            </Text>
            <Text as="p">
              Recycling the container will stop and delete the container and start a new one with the same configuration. All data will be lost.
            </Text>
          </Accordion.Content>
        </Accordion.Item>
      </Accordion.Root>
    </>
  );
}
