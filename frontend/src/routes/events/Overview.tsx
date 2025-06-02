import {
  Container, Flex, Grid, Heading, Skeleton, Tabs, Text,
} from '@radix-ui/themes';
import { FaRankingStar, FaTrophy, FaUserGroup } from 'react-icons/fa6';
import { useSearchParams } from 'react-router';

export default function Overview() {
  const [searchParams, setSearchParams] = useSearchParams();
  const currentTab = searchParams.get('tab') ?? 'challenges';

  return (
    <>
      <Container size="1" my="4">
        <Heading>Event Name</Heading>
        <Text>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit.
          Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
        </Text>
      </Container>

      <Tabs.Root
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
          <Container size="4">
            <Grid columns={{ xs: '1', sm: '2', md: '4' }} gap="4" p="4">
              <Skeleton height="128px" />
              <Skeleton height="128px" />
              <Skeleton height="128px" />
              <Skeleton height="128px" />
              <Skeleton height="128px" />
            </Grid>
          </Container>
        </Tabs.Content>

        <Tabs.Content value="leaderboard">
          <Container size="4">
            <Flex direction="column" gap="2" p="2">
              <Skeleton height="64px" />
              <Skeleton height="64px" />
              <Skeleton height="64px" />
              <Skeleton height="64px" />
              <Skeleton height="64px" />
            </Flex>
          </Container>
        </Tabs.Content>

        <Tabs.Content value="team">
          <Text>Placeholder team info</Text>
        </Tabs.Content>
      </Tabs.Root>
    </>
  );
}
