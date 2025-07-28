import { Container, Tabs } from '@radix-ui/themes';

import { TbStar } from 'react-icons/tb';
import { useParams, useSearchParams } from 'react-router';

import { ChallengeIcon, TeamIcon } from '@/constants';
import { useEvent } from '@/hooks/events';
import EventHeader from 'components/EventHeader';
import HeaderContainer from 'components/HeaderContainer';
import ChallengesTab from './OverviewTabs/ChallengesTab';
import LeaderboardTab from './OverviewTabs/LeaderboardTab';
import TeamTab from './OverviewTabs/TeamTab';

export default function Overview() {
  const [ searchParams, setSearchParams ] = useSearchParams();
  const { idEvent } = useParams();
  const currentTab = searchParams.get('tab') ?? 'challenges';

  const { data } = useEvent(Number(idEvent));

  return (
    <>
      <HeaderContainer>
        {data && (
          <EventHeader
            event={data}
          />
        )}
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
              <ChallengeIcon className="mr-1" />
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
