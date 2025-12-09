import { Flex } from '@radix-ui/themes';
import AdminProvisionerCard from './AdminProvisionerCard';

export default function AdminDashboard() {
  return (
    <>
      <title>Admin Dashboard</title>
      <Flex direction="column" gap="4" className="flex-grow basis-1/2 h-full">
        <AdminProvisionerCard />
      </Flex>
    </>
  );
}
