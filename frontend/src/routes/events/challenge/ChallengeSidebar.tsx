import { useChallenge } from '@/hooks/challenge';
import { useEvent } from '@/hooks/events';
import {
  Box,
  Button,
  Card,
  Flex,
  Heading,
  Inset,
  Skeleton,
  Text,
} from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import ChallengeIcon from 'components/ChallengeIcon';
import RadixMarkdown from 'components/RadixMarkdown';
import { TbArrowLeft } from 'react-icons/tb';
import { Link, useParams } from 'react-router';
import ChallengeHeader from './ChallengeHeader';
import ChallengeQuestion from './ChallengeQuestion';
import ConnectModal from './ConnectModal';
import FeedbackModal from './FeedbackModal';
import HintsModal from './HintsModal';

export default function ChallengeSidebar() {
  const { idEvent, idChallenge } = useParams();

  const { data : event, isLoading : isEventLoading } = useEvent(Number(idEvent));
  const { data, error } = useChallenge(
    Number(idEvent),
    Number(idChallenge),
  );

  const { challenge, questions } = data || {};

  return (
    <Flex direction="column" gap="3" className="shrink-0 grow-0 lg:basis-128">
      <Card className="shrink-0">
        <Inset side="all" className="shrink-0">
          <ChallengeHeader>
            <Flex gap="3" direction="row" align="start" justify="between" mb="3">

              <Button variant="ghost" className="!m-0 !shrink" asChild>
                <Link to={`/events/${idEvent}?tab=challenges`}>
                  <TbArrowLeft />
                  <Skeleton loading={isEventLoading}>
                    <Text>
                      {event?.name || 'Unknown Event'}
                    </Text>
                  </Skeleton>
                </Link>
              </Button>

              <Box flexShrink="0">
                <HintsModal eventId={Number(idEvent)} challengeId={Number(idChallenge)} />
                <FeedbackModal />
              </Box>
            </Flex>

            {error ? (
              <ErrorCallout>
                {error.message}
              </ErrorCallout>
            ) : (
              <Box>
                <Flex direction="row" gap="1" align="center">
                  {challenge?.icon && <Heading size="6"><ChallengeIcon icon={challenge?.icon} /></Heading>}
                  <Skeleton loading={!challenge}>
                    <Heading size="6" className="mt-2">
                      {challenge?.name || 'Unknown Challenge'}
                    </Heading>
                  </Skeleton>
                </Flex>
                <Skeleton loading={!challenge}>
                  <Text color="gray">
                    {challenge?.summary || 'No summary available'}
                  </Text>
                </Skeleton>
              </Box>
            )}

            {challenge && event && (
              <ConnectModal eventId={event.id} challengeId={challenge.id} />
            )}
          </ChallengeHeader>
        </Inset>
      </Card>

      <Card className="!flex flex-col">
        <Inset side="all" className="shrink !overflow-y-auto">
          <Flex direction="column" gap="3" className="p-3">
            {challenge ? (
              <RadixMarkdown>
                {challenge.description}
              </RadixMarkdown>
            ) : (
              <Text>
                <Skeleton loading>
                  {/* Placeholder text to produce a skeleton effect from - actual text is not shown. */}
                  Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                  Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                  Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
                </Skeleton>
              </Text>
            )}

            <Flex direction="column" gap="3">
              {questions?.map((question) => (
                <ChallengeQuestion
                  key={question.id}
                  name={question.name}
                  question={question.body}
                  placeholder={question.placeholder}
                  points={question.points}
                  attemptsRemaining={question.max_attempts}
                  status="unanswered"
                />
              ))}
            </Flex>
          </Flex>
        </Inset>
      </Card>
    </Flex>
  );
}
