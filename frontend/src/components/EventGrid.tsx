import type { Event } from '@/types';
import { Grid, Skeleton } from '@radix-ui/themes';
import EventCard from 'routes/dashboard/EventCard';

export default function EventGrid({ events, loading = false } : {events: Event[], loading?: boolean}) {
  return (
    <Grid
      columns={{
        initial : '1', xs : '1', sm : '2', lg : '3',
      }}
      gap="3"
    >
      {loading && (
      <>
        <Skeleton className="min-h-48 !rounded-lg" />
        <Skeleton className="min-h-48 !rounded-lg" />
        <Skeleton className="min-h-48 !rounded-lg" />
      </>
      )}

      {events?.map((event) => (
        <EventCard
          key={event.id}
          event={event}
        />
      ))}
    </Grid>
  );
}
