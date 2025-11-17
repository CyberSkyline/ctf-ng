import { useEventChallenges, useMyChallenges } from '@/hooks/challenge';
import {
  Card,
  Container,
  Grid,
  Skeleton,
  TextField,
} from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import { keyBy } from 'lodash';
import { useMemo, useState } from 'react';
import { TbSearch } from 'react-icons/tb';
import ChallengeCard from './ChallengeCard';

export default function EventChallenges({ eventId }: {eventId: number}) {
  const { data, error, isLoading } = useEventChallenges(eventId);
  const { data : myChallenges, error : myError } = useMyChallenges(eventId);

  const challengeProgressMap = useMemo(() => keyBy(myChallenges, (progress) => progress.challenge_id), [ myChallenges ]);

  const [ searchQuery, setSearchQuery ] = useState('');

  const filteredChallenges = useMemo(() => {
    if (!data) return [];
    return data.filter((challenge) => challenge.name.toLowerCase().includes(searchQuery.toLowerCase())
      || challenge.summary.toLowerCase().includes(searchQuery.toLowerCase()));
  }, [ data, searchQuery ]);

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
        <TextField.Root placeholder="Search challenges..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}>
          <TextField.Slot>
            <TbSearch height="16" width="16" />
          </TextField.Slot>
        </TextField.Root>
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
          {filteredChallenges.map((challenge) => (
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
