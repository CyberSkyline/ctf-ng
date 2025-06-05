import {
  Container, Tabs,
} from '@radix-ui/themes';
import ChallengesTab from 'routes/events/OverviewTabs/ChallengesTab';
import EventHeader from 'components/event/EventHeader';
import LeaderboardTab from 'routes/events/OverviewTabs/LeaderboardTab';
import TeamTab from 'routes/events/OverviewTabs/TeamTab';

import {
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
        value={currentTab}
        onValueChange={(tab) => {
          setSearchParams((prev) => {
            prev.set('tab', tab);
            return prev;
          });
        }}
      >
        <Container size="2" mb="4">
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
          <ChallengesTab />
        </Tabs.Content>

        <Tabs.Content value="leaderboard">
          <LeaderboardTab />
        </Tabs.Content>

        <Tabs.Content value="team">
          <TeamTab />
        </Tabs.Content>
      </Tabs.Root>
    </>
  );
}
