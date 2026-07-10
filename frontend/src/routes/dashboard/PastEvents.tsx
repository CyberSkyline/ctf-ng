import { useMyEvents } from '@/hooks/events';
import { Grid, Heading } from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import Accordion from 'components/Accordion';
import { useMemo } from 'react';
import { chain } from 'lodash';
import EventCard from './EventCard';

export default function PastEvents() {
  const { data, error } = useMyEvents();
  const pastEvents = data?.filter((event) => event.end_time && new Date() > event.end_time);

  const groupedEvents = useMemo(() => chain(pastEvents)
    .sortBy((event) => event.start_time?.getTime() || 0)
    .groupBy((event) => event.start_time?.getFullYear()?.toString() || 'Unknown')
    .toPairs()
    .reverse()
    .value(), [ pastEvents ]);

  if (error) {
    return (
      <>
        <Heading size="6">Your Past Events</Heading>
        <ErrorCallout>{error.message}</ErrorCallout>
      </>
    );
  }

  if (pastEvents === undefined || pastEvents.length === 0) {
    // Show nothing if there are no past events or if data is still loading
    return null;
  }

  return (
    <>
      <Heading size="6">Your Past Events</Heading>

      <Accordion.Root type="multiple" defaultValue={groupedEvents.length ? [ groupedEvents[0][0] ] : []}>
        {groupedEvents.map(([ year, eventsInYear ]) => (
          <Accordion.Item key={year} value={year}>
            <Accordion.Header>
              <Accordion.Trigger>
                {year}
              </Accordion.Trigger>
            </Accordion.Header>

            <Accordion.Content>
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
            </Accordion.Content>
          </Accordion.Item>
        ))}
      </Accordion.Root>
    </>
  );
}
