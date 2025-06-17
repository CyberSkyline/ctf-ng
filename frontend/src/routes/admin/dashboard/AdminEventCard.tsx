import { Card, Flex, Heading } from '@radix-ui/themes';
import Statistic from 'components/admin/Statistic';
import { TbLink } from 'react-icons/tb';
import { Link } from 'react-router';

/**
 * Admin dashboard card for information about an active event.
 */
export default function AdminEventCard({ id }: {id: string}) {
  return (
    <Card>
      <Heading>
        {id}
        <Link to={`/admin/events?id=${id}`}>
          <TbLink className="inline ms-1 text-(--gray-10)" />
        </Link>
      </Heading>

      <Flex gap="4">
        <Statistic label="Online" value={1} />
        <Statistic label="Registered" value={2} />
        <Statistic label="Submissions" value={3} />
      </Flex>
    </Card>
  );
}
