import { useEvent } from '@/hooks/events';
import {
  Flex, Heading, Spinner,
} from '@radix-ui/themes';
import { Link, useSearchParams } from 'react-router';
import Statistic from 'components/Statistic';
import { ErrorCallout } from 'components/Callouts';
import { EventIcon } from '@/constants';
import AdminDataList from 'components/AdminDataList';
import AdminChallengeCard from './AdminChallengeCard';

export default function EventSidebar() {
  const [searchParams] = useSearchParams();

  const eventId = Number(searchParams.get('id'));
  const { data, error, isLoading } = useEvent(eventId);

  if (isLoading) {
    return (
      <Spinner />
    );
  }

  if (error) {
    return (
      <ErrorCallout>{error.message}</ErrorCallout>
    );
  }

  if (!eventId || !data) {
    return (
      <Flex direction="column" align="center" justify="center" className="w-full h-full">
        <EventIcon className="text-(--gray-9) text-9xl" />
        <Heading className="text-(--gray-9)" size="4">
          Select an event to view details.
        </Heading>
      </Flex>
    );
  }

  return (
    <>
      <Heading>{data.event.name}</Heading>

      <AdminDataList data={data.event} />

      <Flex direction="row" gap="4">
        <Link to={`/admin/teams?event=${data.event.id}`}><Statistic value={data.event.team_count} label="Teams" /></Link>
        <Statistic value={data.event.total_members} label="Users" />
      </Flex>
      <Heading>Challenges</Heading>
      <AdminChallengeCard />
    </>
  );
}
