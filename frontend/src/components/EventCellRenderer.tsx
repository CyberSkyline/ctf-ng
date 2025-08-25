import { EventIcon } from '@/constants';
import { useAdminEvent } from '@/hooks/events';
import { Skeleton } from '@radix-ui/themes';
import Entity from './Entity';

export default function EventCellRenderer({ value : eventId }: { value: number }) {
  const { data, error, isLoading } = useAdminEvent(eventId);

  if (isLoading) {
    return <Skeleton>Loading...</Skeleton>;
  }

  if (error) {
    return (
      <span>
        Error:
        {error.message}
      </span>
    );
  }

  return (
    <Entity icon={EventIcon} to={`/admin/events?id=${eventId}`} label={data?.name ?? 'Unknown Event'} />
  );
}
