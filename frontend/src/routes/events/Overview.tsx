import {
  Container, Flex, Grid, Skeleton, Tabs, Text,
  TextField,
} from '@radix-ui/themes';
import ChallengeCard from 'components/event/ChallengeCard';
import EventHeader from 'components/event/EventHeader';
import { FaSearch } from 'react-icons/fa';
import {
  FaCode,
  FaRankingStar, FaTrophy, FaUserGroup,
} from 'react-icons/fa6';
import { useSearchParams } from 'react-router';

export default function Overview() {
  const [searchParams, setSearchParams] = useSearchParams();
  const currentTab = searchParams.get('tab') ?? 'challenges';

  return (
    <>
      <EventHeader
        name="Event Name"
        description="Lorem ipsum dolor sit amet, consectetur adipiscing elit."
      />

      <Tabs.Root
        mx="4"
        value={currentTab}
        onValueChange={(tab) => {
          setSearchParams((prev) => {
            prev.set('tab', tab);
            return prev;
          });
        }}
      >
        <Container size="2">
          <Tabs.List className="*:!basis-0 *:!grow" loop={false}>
            <Tabs.Trigger value="challenges">
              <FaTrophy className="mr-1" />
              Challenges
            </Tabs.Trigger>
            <Tabs.Trigger value="leaderboard">
              <FaRankingStar className="mr-1" />
              Leaderboard
            </Tabs.Trigger>
            <Tabs.Trigger value="team">
              <FaUserGroup className="mr-1" />
              Team
            </Tabs.Trigger>
          </Tabs.List>
        </Container>

        <Tabs.Content value="challenges">
          { /* TODO: extract to a separate component */ }

          <Container size="2">
            { /* TODO: make search functional once real data is available */ }
            <TextField.Root placeholder="Search challenges..." my="4">
              <TextField.Slot>
                <FaSearch height="16" width="16" />
              </TextField.Slot>
            </TextField.Root>
          </Container>
          <Container size="4">
            <Grid columns={{ xs: '1', sm: '2', md: '3' }} gap="4">
              {/* Placeholder challenges to demo UI */}
              {[...Array(8)].map((_, index) => (
                <ChallengeCard
                  id={index.toString()}
                  name="Challenge Name"
                  description="Lorem ipsum dolor sit amet, consectetur adipiscing elit."
                  icon={FaCode}
                  points={1000}
                  completed={index % 2 === 0} // Example completion status
                  // using index as key for test data. replace with unique id once present
                  // eslint-disable-next-line react/no-array-index-key
                  key={index}
                />
              ))}
            </Grid>
          </Container>
        </Tabs.Content>

        <Tabs.Content value="leaderboard">
          { /* Placeholder leaderboard */ }
          <Container size="4">
            <Flex direction="column" gap="2" py="2">
              <Skeleton height="64px" />
              <Skeleton height="64px" />
              <Skeleton height="64px" />
              <Skeleton height="64px" />
              <Skeleton height="64px" />
            </Flex>
          </Container>
        </Tabs.Content>

        <Tabs.Content value="team">
          { /* Placeholder team info */ }
          <Text>Placeholder team info</Text>
        </Tabs.Content>
      </Tabs.Root>
    </>
  );
}
