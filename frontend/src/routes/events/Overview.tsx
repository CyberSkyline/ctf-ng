import {
  Container, Tabs,
} from '@radix-ui/themes';

import { TbCube, TbStar } from 'react-icons/tb';
import { useSearchParams } from 'react-router';

import EventHeader from 'components/EventHeader';
import HeaderContainer from 'components/HeaderContainer';
import { TeamIcon } from '@/constants';
import LeaderboardTab from './OverviewTabs/LeaderboardTab';
import ChallengesTab from './OverviewTabs/ChallengesTab';
import TeamTab from './OverviewTabs/TeamTab';

export default function Overview() {
  const [ searchParams, setSearchParams ] = useSearchParams();
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
              <TeamIcon className="mr-1" />
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
