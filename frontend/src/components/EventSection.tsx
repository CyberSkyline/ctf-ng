import EventCard from './EventCard';
import { Grid, Heading } from '@radix-ui/themes';
import type { Event } from '@/types';

export default function EventSection({ year, eventsInYear }: { year?: string, eventsInYear: Event[]}) {
  return (
    <section key={year}>
      {year !== 'Unknown' && (
        <Heading className="!mb-3" size="4">
          {year}
        </Heading>
      )}
      <Grid
        columns={{
          initial : '1', xs : '1', sm : '2', lg : '3',
        }}
        gap="3"
      >
        {eventsInYear.map((event) => (
          <EventCard
            key={event.id}
            event={event}
          />
        ))}
      </Grid>
    </section>
  );
}
