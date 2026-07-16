import type { Event } from '@/types';
import {
  Box,
  Flex,
  Grid,
  Heading,
  Skeleton,
} from '@radix-ui/themes';
import { groupBy } from 'lodash';
import { Fragment, useMemo } from 'react';
import EventSection from './EventSection';

export default function EventGrid({ events, loading = false, group = false } : { events: Event[], loading?: boolean, group?: boolean }) {
  const sortedEvents = useMemo(() => events.slice().sort((a, b) => {
    const dateA = a.start_time?.getTime() || 0;
    const dateB = b.start_time?.getTime() || 0;
    return dateA - dateB;
  }), [ events ]);

  const groupedEvents = useMemo(() => {
    if (!group) return { Unknown : sortedEvents };
    return groupBy(sortedEvents, (event) => event.start_time?.getFullYear()?.toString() || 'Unknown');
  }, [ sortedEvents, group ]);

  return (
    <Flex direction="column" gap="8">
      {loading && (
        <Box>
          {group && <Heading className="!mb-3" size="4"><Skeleton>YYYY</Skeleton></Heading>}
          <Grid
            columns={{
              initial : '1', xs : '1', sm : '2', lg : '3',
            }}
            gap="3"
          >
            <Skeleton className="min-h-48 !rounded-lg" />
            <Skeleton className="min-h-48 !rounded-lg" />
            <Skeleton className="min-h-48 !rounded-lg" />
          </Grid>
        </Box>
      )}
      {[ ...Object.entries(groupedEvents) ]
        .reverse()
        .map(([ year, eventsInYear ]) => (
          <Fragment key={year}>
            <EventSection
              eventsInYear={eventsInYear}
            />
          </Fragment>
        ))}
    </Flex>
  );
}
