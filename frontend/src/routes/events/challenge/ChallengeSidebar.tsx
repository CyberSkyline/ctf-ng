import { useChallenge } from '@/hooks/challenge';
import { useEvent, useMyTeam } from '@/hooks/events';
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
import Timer from 'components/Timer';
import { groupBy } from 'lodash';
import { useState } from 'react';
import { TbArrowLeft } from 'react-icons/tb';
import { Link, useParams } from 'react-router';
import { mutate } from 'swr';
import ChallengeHeader from './ChallengeHeader';
import ChallengeQuestion from './ChallengeQuestion';
import ConnectModal from './ConnectModal';
import FeedbackModal from './FeedbackModal';
import FeedbackPrompt from './FeedbackPrompt';
import HintsModal from './HintsModal';
import HistoryModal from './HistoryModal';
import NotConnectedWarning from './NotConnectedWarning';

export default function ChallengeSidebar() {
  const { idEvent, idChallenge } = useParams();

  const { data : event, isLoading : isEventLoading } = useEvent(Number(idEvent));
  const { data : team } = useMyTeam(Number(idEvent));
  const { data, error } = useChallenge(
    Number(idEvent),
    Number(idChallenge),
  );

  const [ provisioningError, setProvisioningError ] = useState<Error | undefined>();

  const {
    challenge, questions, hints, attempts,
  } = data || {};

  const groupedAttempts = groupBy(attempts || [], 'question_id');

  return (
    <Flex direction="column" gap="3" className="shrink-0 grow-0 lg:basis-128 h-full">
      <title>{`${challenge?.name || 'Challenge'}`}</title>
      <Card className="shrink-0">
        <Inset side="all" className="shrink-0">
          <ChallengeHeader>
            <Flex gap="3" direction="row" align="center" justify="between" mb="3">

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

              {team && team.end_time && (
                <Timer
                  target={new Date(team.end_time)}
                  size="3"
                  onEnd={() => {
                    // Refresh SWR state on timer end
                    mutate(`/permissions/${idEvent}/me`);
                    mutate(`/events/${idEvent}/me/team`);
                    mutate(`/users/me/teams`);
                  }}
                />
              ) }
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
              <>
                {provisioningError && <ErrorCallout className="mt-3">{provisioningError.message}</ErrorCallout>}
                <Flex direction="row" gap="2" mt="3" align="center" justify="between">
                  <ConnectModal
                    eventId={event.id}
                    challengeId={challenge.id}
                    isTeam={event.max_team_size > 1}
                    onError={setProvisioningError}
                  />
                  <Box flexShrink="0">
                    {hints && hints.length > 0 && <HintsModal eventId={event.id} challengeId={challenge.id} />}
                    {attempts && <HistoryModal isTeam={event.max_team_size > 1} attempts={attempts} />}
                    <FeedbackModal eventId={event.id} challengeId={challenge.id} />
                  </Box>
                </Flex>
              </>
            )}
          </ChallengeHeader>
        </Inset>
      </Card>

      {challenge && <FeedbackPrompt eventId={challenge.event_id} challengeId={challenge.id} /> }
      {challenge && <NotConnectedWarning challenge={challenge} /> }

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
              {challenge && questions?.map((question) => (
                <ChallengeQuestion
                  key={question.id}
                  eventId={challenge.event_id}
                  question={question}
                  attempts={groupedAttempts[question.id] || []}
                />
              ))}
            </Flex>
          </Flex>
        </Inset>
      </Card>
    </Flex>
  );
}
