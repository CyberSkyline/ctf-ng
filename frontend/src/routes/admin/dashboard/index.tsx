import {
  Callout, Flex,
} from '@radix-ui/themes';
import {
  TbAlertTriangle,
} from 'react-icons/tb';
import AdminEventCard from './AdminEventCard';
import AdminProvisionerCard from './AdminProvisionerCard';
import AdminActivityCard from './AdminActivityCard';
import AdminOverviewCard from './AdminOverviewCard';

/**
 * Admin dashboard with system monitoring and important metrics.
 */
export default function AdminDashboard() {
  return (
    <>
      <Callout.Root
        color="amber"
        variant="surface"
        mb="4"
      >
        <Callout.Icon>
          <TbAlertTriangle />
        </Callout.Icon>
        <Callout.Text>
          Something bad happened!
        </Callout.Text>
      </Callout.Root>

      <Flex direction={{ initial: 'column', lg: 'row' }} gap="4">
        <Flex direction="column" gap="4" className="flex-grow basis-1/2 h-full">
          <AdminOverviewCard />
          <AdminActivityCard />
          <AdminProvisionerCard />
        </Flex>
        <Flex direction="column" gap="4" flexGrow="1" flexBasis="50%">
          <AdminEventCard id="event1" />
          <AdminEventCard id="event2" />
          <AdminEventCard id="event3" />
        </Flex>
      </Flex>

    </>
  );
}
