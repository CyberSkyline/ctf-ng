import {
  Container, Tabs,
} from '@radix-ui/themes';
import ChallengesTab from 'routes/events/OverviewTabs/ChallengesTab';
import EventHeader from 'components/event/EventHeader';
import LeaderboardTab from 'routes/events/OverviewTabs/LeaderboardTab';
import TeamTab from 'routes/events/OverviewTabs/TeamTab';

import { useSearchParams } from 'react-router';
import HeaderContainer from 'components/HeaderContainer';
import { TbCube, TbStar, TbUsersGroup } from 'react-icons/tb';

export default function Overview() {
  const [searchParams, setSearchParams] = useSearchParams();
  const currentTab = searchParams.get('tab') ?? 'challenges';

  return (
    <>
      <HeaderContainer>
        <EventHeader
          name="Event Name"
          description="Lorem ipsum dolor sit amet, consectetur adipiscing elit."
          state="upcoming"
        />
      </HeaderContainer>

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
              <TbCube className="mr-1" />
              Challenges
            </Tabs.Trigger>
            <Tabs.Trigger value="leaderboard">
              <TbStar className="mr-1" />
              Leaderboard
            </Tabs.Trigger>
            <Tabs.Trigger value="team">
              <TbUsersGroup className="mr-1" />
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
