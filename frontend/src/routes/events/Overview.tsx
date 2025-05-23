import Container from 'components/layout/Container';
import { TabItem, Tabs } from 'flowbite-react';
import { useMemo } from 'react';
import { FaRankingStar, FaTrophy, FaUserGroup } from 'react-icons/fa6';
import { useParams, useSearchParams } from 'react-router';

export default function Overview() {
  const { idEvent } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();

  // eventually this will need logic to adjust the tab list dynamically based on event properties
  // i.e. if the event is individual, the team tab shouldn't be present
  const tabs = useMemo(() => [
    {
      key: 'challenges',
      title: 'Challenges',
      icon: FaTrophy,
      content: <span>Placeholder Challenges</span>,
    },
    {
      key: 'leaderboard',
      title: 'Leaderboard',
      icon: FaRankingStar,
      content: <span>Placeholder Leaderboard</span>,
    },
    {
      key: 'team',
      title: 'Team',
      icon: FaUserGroup,
      content: <span>Placeholder Team</span>,
    },
  ], []);

  return (
    <Container>
      <h1 className="text-3xl text-white font-bold">{idEvent}</h1>
      <p>Some filler text, start time, stop time, etc.</p>

      <Tabs variant="fullWidth" className="mt-4" onActiveTabChange={(index) => setSearchParams({ tab: tabs[index].key })}>
        {tabs.map((tab) => (
          <TabItem
            key={tab.key}
            // TODO: figure out how to set aria-hidden on icon components passed into flowbite.
            // HoC seems to be the only way to do it, but it's janky and violates many eslint rules
            icon={tab.icon}
            title={tab.title}
            active={searchParams.get('tab') === tab.key}
          >
            {tab.content}
          </TabItem>
        ))}
      </Tabs>
    </Container>
  );
}
