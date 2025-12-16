import {
  Button,
  Container,
  Link as RadixLink,
  Tabs,
} from '@radix-ui/themes';

import { TbArrowRight, TbMessageCircle, TbStar } from 'react-icons/tb';
import { Link, useParams, useSearchParams } from 'react-router';

import { ChallengeIcon, TeamIcon } from '@/constants';
import { useEvent } from '@/hooks/events';
import { useMyEventFeedback } from '@/hooks/feedback';
import { useAuth, useRegistration } from '@/hooks/users';
import { ErrorCallout, InfoCallout } from 'components/Callouts';
import EventHeader from 'components/EventHeader';
import HeaderContainer from 'components/HeaderContainer';
import ChallengesTab from './OverviewTabs/ChallengesTab';
import FeedbackTab from './OverviewTabs/FeedbackTab';
import LeaderboardTab from './OverviewTabs/LeaderboardTab';
import TeamTab from './OverviewTabs/TeamTab';
import RegistrationCard from './RegistrationCard';

export default function Overview() {
  const [ searchParams, setSearchParams ] = useSearchParams();
  const { idEvent } = useParams();
  const eventId = Number(idEvent);

  const { data, error } = useEvent(eventId);
  const { isAuthenticated, isUnauthenticated } = useAuth();
  const {
    isRegistered, isUnregistered, isStarted, isFinished, team,
  } = useRegistration(eventId);

  const challengesTabAvailable = isRegistered;
  const teamTabAvailable = isRegistered && data && data.max_team_size > 1;
  const feedbackAvailable = isRegistered && (isFinished || (isStarted && !team!.end_time));

  const { data : feedback } = useMyEventFeedback(feedbackAvailable ? eventId : null);

  let currentTab = searchParams.get('tab') ?? undefined;
  if (!currentTab) {
    if (isRegistered) {
      currentTab = 'challenges';
    } else if (isUnregistered) {
      currentTab = 'leaderboard';
    } else {
      // if we don't know registration state yet,
      // don't show any tab to avoid flicker once it loads
      currentTab = undefined;
    }
  }

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  return (
    <>
      <title>{`${data?.name || 'Event Detail'}`}</title>
      <HeaderContainer>
        {data && (
          <EventHeader
            event={data}
          >
            {isAuthenticated && data && (
              <RegistrationCard event={data} />
            )}
            {isFinished && feedback === null && (
              <InfoCallout className="max-w-128">
                Please take a moment to provide feedback on your experience so that we can improve future events.
                <br />
                <Button variant="soft" mt="3">
                  <Link to={`/events/${data.id}?tab=feedback`}>
                    Give Feedback
                    <TbArrowRight className="inline ms-1" />
                  </Link>
                </Button>
              </InfoCallout>
            )}
            {isUnauthenticated && (
              <InfoCallout>
                To participate in this event, please
                {' '}
                <RadixLink asChild>
                  <Link to={`/login?redirect=${encodeURIComponent(window.location.pathname + window.location.search)}`}>log in</Link>
                </RadixLink>
                .
              </InfoCallout>
            )}
          </EventHeader>
        )}
      </HeaderContainer>

      <Tabs.Root
        value={currentTab}
        onValueChange={(tab) => {
          if (tab === currentTab) {
            return;
          }
          setSearchParams((prev) => {
            prev.set('tab', tab);
            return prev;
          });
        }}
        activationMode="manual"
      >
        <Container size="2" mb="3">
          <Tabs.List className="*:!basis-0 *:!grow" loop={false}>
            {challengesTabAvailable && (
              <Tabs.Trigger value="challenges">
                <ChallengeIcon className="mr-1" />
                Challenges
              </Tabs.Trigger>
            )}
            <Tabs.Trigger value="leaderboard">
              <TbStar className="mr-1" />
              Leaderboard
            </Tabs.Trigger>
            {teamTabAvailable && (
              <Tabs.Trigger value="team">
                <TeamIcon className="mr-1" />
                Team
              </Tabs.Trigger>
            )}
            {feedbackAvailable && (
              <Tabs.Trigger value="feedback">
                <TbMessageCircle className="mr-1" />
                Feedback
              </Tabs.Trigger>
            )}
          </Tabs.List>
        </Container>

        {challengesTabAvailable && (
          <Tabs.Content value="challenges">
            <ChallengesTab />
          </Tabs.Content>
        )}

        <Tabs.Content value="leaderboard">
          <LeaderboardTab />
        </Tabs.Content>

        {teamTabAvailable && (
          <Tabs.Content value="team">
            <TeamTab />
          </Tabs.Content>
        )}

        {feedbackAvailable && (
          <Tabs.Content value="feedback">
            <FeedbackTab />
          </Tabs.Content>
        )}
      </Tabs.Root>
    </>
  );
}
