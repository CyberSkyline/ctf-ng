import { useProvisionerStats } from '@/hooks/container';
import { Card, Flex, Heading } from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import Statistic from 'components/Statistic';
import AdminPullVncModal from './AdminPullVncModal';

export default function AdminProvisionerCard() {
  const { data, error } = useProvisionerStats();

  if (error) {
    return (
      <ErrorCallout>
        Failed to load provisioner data.
        <br />
        {error.message}
      </ErrorCallout>
    );
  }

  return (
    <Card>
      <Heading>
        <Flex direction="row" align="center" justify="between">
          Provisioner
          <AdminPullVncModal />
        </Flex>
      </Heading>
      <Flex gap="4" mt="3">
        <Statistic
          label="Containers Running"
          value={data?.containers_running || 0}
          description="Total number of containers running."
        />
        <Statistic
          label="CPUs"
          value={data?.cpus || 0}
          description="Total available logical processors."
        />
        <Statistic
          label="Memory"
          value={`${((data?.memory || 0) / (1024 * 1024 * 1024)).toFixed(2)}GiB`}
          description="Total available memory."
        />
      </Flex>
    </Card>
  );
}
