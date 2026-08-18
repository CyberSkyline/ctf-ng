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
          {data?.length > 1 ? 'Provisioners' : 'Provisioner'}
          <AdminPullVncModal />
        </Flex>
      </Heading>
      { data?.map((host: { containers_running: number; os: string; cpus: number, memory: number }, index: number) => (
        <Flex key={index} gap="4" mt="3">
          <Statistic
            label="Host"
            value={host?.ip || ''}
            description="Host ip"
          />
          <Statistic
            label="Containers Running"
            value={host?.containers_running || 0}
            description="Total number of containers running."
          />
          <Statistic
            label="CPUs"
            value={host?.cpus || 0}
            description="Total available logical processors."
          />
          <Statistic
            label="Memory"
            value={`${((host?.memory || 0) / (1024 * 1024 * 1024)).toFixed(2)}GiB`}
            description="Total available memory."
          />
        </Flex>
      ))}
    </Card>
  );
}
