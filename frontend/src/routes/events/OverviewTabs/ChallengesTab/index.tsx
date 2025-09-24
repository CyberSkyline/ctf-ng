import { useEventChallenges, useMyChallenges } from '@/hooks/challenge';
import { useMyTeam } from '@/hooks/events';
import {
  Container,
  Grid,
  Text,
  TextField,
} from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import { keyBy } from 'lodash';
import { useMemo, useState } from 'react';
import { TbCancel, TbSearch } from 'react-icons/tb';
import { useParams } from 'react-router';
import ChallengeCard from './ChallengeCard';

export default function ChallengesTab() {
  const { idEvent } = useParams<{idEvent: string}>();
  const { data, error } = useEventChallenges(Number(idEvent));
  const { data : myChallenges, error : myError } = useMyChallenges(Number(idEvent));

  const challengeProgressMap = useMemo(() => keyBy(myChallenges, (progress) => progress.challenge_id), [ myChallenges ]);

  const [ searchQuery, setSearchQuery ] = useState('');

  const filteredChallenges = useMemo(() => {
    if (!data) return [];
    return data.filter((challenge) => challenge.name.toLowerCase().includes(searchQuery.toLowerCase())
      || challenge.summary.toLowerCase().includes(searchQuery.toLowerCase()));
  }, [ data, searchQuery ]);

  // NAIVE PERMISSION CHECK - SHOULD BE BASED ON CAN_VIEW_CHALLENGES
  // For now, just check if the user's team has a start timestamp
  const { data : myTeam } = useMyTeam(Number(idEvent));
  const challengesAvailable = myTeam?.start_timestamp;

  if (!challengesAvailable) {
    return (
      <Container size="2" className="text-center">
        <TbCancel className="inline text-9xl my-8" />
        <br />
        <Text size="3" color="gray">
          Challenges are not available until your team has started the event.
        </Text>
      </Container>
    );
  }

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
