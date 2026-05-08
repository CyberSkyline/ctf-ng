import { useEventChallenges, useMyChallenges } from '@/hooks/challenge';
import {
  Button,
  Card,
  Container,
  Flex,
  Grid,
  Skeleton,
  Text,
  TextField,
  Tooltip,
} from '@radix-ui/themes';
import { ErrorCallout, InfoCallout } from 'components/Callouts';
import { groupBy, keyBy } from 'lodash';
import {
  useEffect,
  useId,
  useMemo,
  useState,
} from 'react';
import {
  TbFilter,
  TbFilterFilled,
  TbFilterOff,
  TbSearch,
} from 'react-icons/tb';
import MiniSearch from 'minisearch';
import { getTaxonomy, prettyPrintTag } from '@/util';
import { COLOR_NEGATIVE } from '@/constants';
import ChallengeCard from './ChallengeCard';
import FilterPanel from './FilterPanel';

export default function EventChallenges({ eventId }: {eventId: number}) {
  const { data = [], error, isLoading } = useEventChallenges(eventId);
  const { data : myChallenges, error : myError } = useMyChallenges(eventId);

  const challengeMap = useMemo(() => keyBy(data, (challenge) => challenge.id), [ data ]);
  const challengeProgressMap = useMemo(() => keyBy(myChallenges, (progress) => progress.challenge_id), [ myChallenges ]);

  // current search query from the input field
  const [ searchQuery, setSearchQuery ] = useState('');

  // debounced query to reduce CPU usage and potential jank while typing
  const [ debouncedQuery, setDebouncedQuery ] = useState('');
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(searchQuery), 200);
    return () => clearTimeout(timer);
  }, [ searchQuery ]);

  // set of tags that are currently selected for filtering
  const [ selectedTags, setSelectedTags ] = useState(new Set<string>());
  // group selected tags by taxonomy for filtering
  const selectedTagsByTaxonomy = useMemo(() => groupBy(Array.from(selectedTags), getTaxonomy), [ selectedTags ]);

  // whether filter UI should be shown
  const [ showFilters, setShowFilters ] = useState(false);
  const filterPanelId = useId();

  // Build the search index based on data
  // important to memoize, this is expensive
  const miniSearch = useMemo(() => {
    if (!data) return null;
    const search = new MiniSearch({
      fields : [ 'name', 'summary', 'description', 'tags' ],
      extractField(document, fieldName) {
        if (fieldName === 'tags') {
          // join tags into a single pretty-printed string for indexing
          return document.tags.map(prettyPrintTag).join(' ');
        }
        return document[fieldName] || '';
      },
    });
    search.addAll(data);
    return search;
  }, [ data ]);

  // Actual search/filter process begins here:
  // This is done in multiple memo steps so changes to tag selection won't require re-running the search

  // produce search results from the debounced query
  // since the search index is built once to cover all data, run the search first
  const searchResults = useMemo(() => {
    // skip the actual search if query is empty or we don't have an index (no data yet)
    if (debouncedQuery.trim() === '' || !miniSearch) return data;

    return miniSearch.search(debouncedQuery, {
      prefix : true,
      fuzzy : 0.2,
      boost : { name : 2 },
    }).map((result) => challengeMap[result.id])
      .filter(Boolean); // guard against undefined results if index somehow gets out of sync
  }, [ miniSearch, debouncedQuery, data, challengeMap ]);

  // apply tag filters to the search results. OR within taxonomy, AND across taxonomies
  const filteredResults = useMemo(() => searchResults.filter(
    (challenge) => Object.values(selectedTagsByTaxonomy).every(
      (tagsInTaxonomy) => tagsInTaxonomy.some(
        (tag) => challenge.tags.includes(tag),
      ),
    ),
  ), [ searchResults, selectedTagsByTaxonomy ]);

  if (error) {
    return (
      <Container size="4">
        <ErrorCallout>{error.message}</ErrorCallout>
      </Container>
    );
  }

  return (
    <>
      <Container size="2" mb="3">
        <Flex direction="row" gap="1">
          <TextField.Root
            placeholder="Search challenges..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="grow"
          >
            <TextField.Slot>
              <TbSearch height="16" width="16" />
            </TextField.Slot>
          </TextField.Root>
          <Button
            variant={selectedTags.size > 0 ? 'solid' : 'surface'}
            color={showFilters || selectedTags.size > 0 ? undefined : 'gray'}
            onClick={() => setShowFilters((prev) => !prev)}
            className="tabular-nums!"
            aria-label={selectedTags.size > 0 ? `Filters (${selectedTags.size} active)` : 'Filters'}
            aria-expanded={showFilters}
            aria-controls={filterPanelId}
          >
            {selectedTags.size > 0 ? <TbFilterFilled /> : <TbFilter />}
            Filter
          </Button>
        </Flex>
        {showFilters && (
          <FilterPanel
            challenges={data}
            selectedTags={selectedTags}
            onTagToggle={(tag) => {
              setSelectedTags((prev) => {
                const newSet = new Set(prev);
                if (newSet.has(tag)) {
                  newSet.delete(tag);
                } else {
                  newSet.add(tag);
                }
                return newSet;
              });
            }}
            id={filterPanelId}
          />
        )}
        <Flex direction="row" gap="2" justify="between" mt="1">
          <Text
            color="gray"
            size="2"
            role="status"
            aria-live="polite"
            aria-atomic="true"
          >
            Showing
            {' '}
            {filteredResults.length}
            {' '}
            of
            {' '}
            {data.length}
            {' '}
            challenge
            {data.length !== 1 && 's'}
          </Text>
          {selectedTags.size > 0 && (
            <Flex direction="row" gap="1" align="center">
              <Text size="2" color="gray">
                {selectedTags.size}
                {' '}
                filter
                {selectedTags.size !== 1 && 's'}
                {' '}
                active
              </Text>
              <Tooltip content="Clear filters">
                <Button
                  variant="ghost"
                  color={COLOR_NEGATIVE}
                  size="1"
                  className="m-0! p-1!"
                  onClick={() => setSelectedTags(new Set())}
                >
                  <TbFilterOff />
                </Button>
              </Tooltip>
            </Flex>
          )}
        </Flex>
        {filteredResults.length === 0 && !isLoading && (
          <InfoCallout className="mt-3">
            No challenges found.
          </InfoCallout>
        )}
      </Container>
      <Container size="4">
        {myError && (<ErrorCallout className="mb-3">Failed to load your progress.</ErrorCallout>)}
        <Grid columns={{ xs : '1', sm : '2', md : '3' }} gap="3">
          {isLoading && (
            <>
              <Skeleton><Card className="!h-18" /></Skeleton>
              <Skeleton><Card className="!h-18" /></Skeleton>
              <Skeleton><Card className="!h-18" /></Skeleton>
            </>
          )}
          {filteredResults.map((challenge) => (
            <ChallengeCard
              challenge={challenge}
              progress={challengeProgressMap[challenge.id]}
              key={challenge.id}
            />
          ))}
        </Grid>
      </Container>
    </>
  );
}
