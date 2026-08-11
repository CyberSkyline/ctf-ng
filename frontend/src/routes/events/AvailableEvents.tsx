import { useCompetitionEvents } from '@/hooks/events';
import type { Event } from '@/types';
import {
  Box,
  Container,
  Flex,
  Grid,
  Heading,
  Skeleton,
  Link as RadixLink,
} from '@radix-ui/themes';
import { InfoCallout, ErrorCallout, WarningCallout } from 'components/Callouts';
import HeaderContainer from 'components/HeaderContainer';
import Accordion from 'components/Accordion';
import EventSection from 'components/EventSection';
import { Fragment, useMemo, useState } from 'react';
import { chain } from 'lodash';
import { useAuth } from '@/hooks/users';
import { Link } from 'react-router';
import SearchField from './SearchField';

function LoadingBox() {
  return (
    <Box>
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
  );
}

export default function AvailableEvents() {
  const { data : events, error, isLoading } = useCompetitionEvents();
  const { isUnauthenticated } = useAuth();

  const [ search, setSearch ] = useState('');

  const filteredEvents = useMemo(() => {
    if (!events) return [];

    const query = search.trim().toLowerCase();
    if (!query) return events;

    return events.filter(({ name }) => name.toLowerCase().includes(query));
  }, [ events, search ]);

  const { upcomingEvents, groupedPastEvents } = useMemo(() => {
    const now = new Date();

    const upcoming: Event[] = [];
    const past: Event[] = [];

    filteredEvents.forEach((event) => {
      if (!event.end_time || new Date(event.end_time) > now) {
        upcoming.push(event);
      } else {
        past.push(event);
      }
    });

    return {
      upcomingEvents : upcoming,
      groupedPastEvents : chain(past)
        .sortBy((event) => (event.start_time ? new Date(event.start_time).getTime() : 0))
        .groupBy(
          (event) => (event.start_time ? new Date(event.start_time).getFullYear().toString() : 'Unknown'),
        )
        .toPairs()
        .reverse()
        .value(),
    };
  }, [ filteredEvents ]);

  return (
    <>
      <title>Events</title>
      <HeaderContainer>
        <Heading size="9">Events</Heading>
      </HeaderContainer>

      <Container size="4" my="8">
        {error && (<ErrorCallout className="mb-3">{error.message}</ErrorCallout>)}

        {isUnauthenticated && (
          <InfoCallout className="mb-3">
            To participate in events, please
            {' '}
            <RadixLink asChild>
              <Link to={`/login?redirect=${encodeURIComponent(window.location.pathname + window.location.search)}`}>log in</Link>
            </RadixLink>
            .
          </InfoCallout>
        )}

        <SearchField
          placeholder="Search Events..."
          onSearch={setSearch}
          className="mb-7"
        />

        <Heading size="6" className="!mb-3">Upcoming Events</Heading>
        {isLoading && <LoadingBox />}

        {!isLoading && upcomingEvents.length === 0 && (
          <WarningCallout>
            {search === ''
              ? 'No Upcoming Events. Please check back later.'
              : 'No Upcoming Events match the search criteria.'}
          </WarningCallout>
        )}

        {!isLoading && upcomingEvents.length > 0 && (
          <EventSection
            eventsInYear={upcomingEvents}
          />
        )}

        <Heading size="6" className="!mb-3 !mt-7">Past Events</Heading>
        {isLoading && <LoadingBox />}

        {!isLoading && groupedPastEvents.length === 0 && (
          <WarningCallout>
            {search === ''
              ? 'No Past Events.'
              : 'No Past Events match the search criteria.'}
          </WarningCallout>
        )}

        {!isLoading && groupedPastEvents.length > 0 && search === '' && (
          <Accordion.Root
            className="mt-3"
            type="multiple"
            defaultValue={[ groupedPastEvents[0][0] ]}
          >
            <Accordion.Item value="prevYear">
              <Accordion.Header>
                <Accordion.Trigger>
                  {groupedPastEvents[0][0]}
                </Accordion.Trigger>
              </Accordion.Header>

              <Accordion.Content>
                {groupedPastEvents.slice(0, 1).map(([ year, eventsInYear ]) => (
                  <Fragment key={year}>
                    <EventSection
                      eventsInYear={eventsInYear}
                    />
                  </Fragment>
                ))}
              </Accordion.Content>
            </Accordion.Item>

            {groupedPastEvents.length > 1 && (
              <Accordion.Item value="archive">
                <Accordion.Header>
                  <Accordion.Trigger>
                    Archived Events
                  </Accordion.Trigger>
                </Accordion.Header>

                <Accordion.Content>
                  <Flex gap="3" direction="column">
                    {groupedPastEvents.slice(1).map(([ year, eventsInYear ]) => (
                      <Fragment key={year}>
                        <EventSection
                          year={year}
                          eventsInYear={eventsInYear}
                        />
                      </Fragment>
                    ))}
                  </Flex>
                </Accordion.Content>
              </Accordion.Item>
            )}
          </Accordion.Root>
        )}

        {!isLoading && groupedPastEvents.length > 0 && search !== '' && (
          <Flex gap="3" direction="column">
            {groupedPastEvents.map(([ year, eventsInYear ]) => (
              <EventSection
                key={year}
                year={year}
                eventsInYear={eventsInYear}
              />
            ))}
          </Flex>
        )}
      </Container>
    </>
  );
}
