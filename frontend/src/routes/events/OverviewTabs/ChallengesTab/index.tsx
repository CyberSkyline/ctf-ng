import { useEventChallenges, useMyChallenges } from '@/hooks/challenge';
import {
  Container,
  Grid,
  Text,
  TextField,
} from '@radix-ui/themes';
import _ from 'lodash';
import { useMemo, useState } from 'react';
import { TbCancel, TbSearch } from 'react-icons/tb';
import { useParams } from 'react-router';
import ChallengeCard from './ChallengeCard';

export default function ChallengesTab() {
  const { idEvent } = useParams<{idEvent: string}>();
  const { data } = useEventChallenges(Number(idEvent));
  const { data : myChallenges } = useMyChallenges(Number(idEvent));

  const challengeProgressMap = useMemo(() => _.keyBy(myChallenges, (progress) => progress.challenge_id), [ myChallenges ]);

  const [ searchQuery, setSearchQuery ] = useState('');

  const filteredChallenges = useMemo(() => {
    if (!data) return [];
    return data.filter((challenge) => challenge.name.toLowerCase().includes(searchQuery.toLowerCase())
      || challenge.summary.toLowerCase().includes(searchQuery.toLowerCase()));
  }, [ data, searchQuery ]);

  // Are we in the event window/team start time?
  const challengesAvailable = true;

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

  return (
    <>
      <Container size="2" mb="4">
        <TextField.Root placeholder="Search challenges..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}>
          <TextField.Slot>
            <TbSearch height="16" width="16" />
          </TextField.Slot>
        </TextField.Root>
      </Container>
      <Container size="4">
        <Grid columns={{ xs : '1', sm : '2', md : '3' }} gap="4">
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
