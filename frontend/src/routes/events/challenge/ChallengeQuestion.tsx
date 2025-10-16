import {
  Button,
  Flex,
  Heading,
  Text,
  TextField,
} from '@radix-ui/themes';
import RadixMarkdown from 'components/RadixMarkdown';
import { Form } from 'radix-ui';
import { TbFlag2 } from 'react-icons/tb';
import { twMerge } from 'tailwind-merge';

import {
  COLOR_NEGATIVE,
  COLOR_POSITIVE,
  COLOR_QUESTION,
  type AccentColor,
} from '@/constants';
import { submitFlag } from '@/hooks/challenge';
import { useEventPermission } from '@/hooks/permissions';
import type { Attempt, Question } from '@/types';
import RequireEventPermission from 'components/RequireEventPermission';
import { startCase } from 'lodash';
import { useCallback } from 'react';

export default function ChallengeQuestion({
  eventId,
  question,
  attempts,
}: {
  eventId: number;
  question: Question;
  attempts: Attempt[];
}) {
  const {
    id, name, points, body, max_attempts : maxAttempts, placeholder, challenge_id : challengeId,
  } = question;

  const { denied } = useEventPermission('CAN_PLAY_CHALLENGES', eventId);

  const handleSubmit = useCallback((event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const target = event.currentTarget;
    const { flag } = Object.fromEntries(new FormData(event.currentTarget));

    return submitFlag(challengeId, id, flag as string)
      .finally(() => {
        // clear the form after submission
        target.reset();
      });
  }, [ challengeId, id ]);

  const attemptsRemaining = maxAttempts - attempts.length;

  let status: 'unanswered' | 'correct' | 'incorrect' = 'unanswered';
  let color: AccentColor | undefined;

  if (attempts.find((attempt) => attempt.is_correct)) {
    status = 'correct';
    color = COLOR_POSITIVE;
  } else if (attempts.length > 0) {
    status = 'incorrect';
    color = COLOR_NEGATIVE;
  }

  return (
    <Flex direction="column">
      <Flex direction="row" gap="2" align="center" justify="start">
        <Heading size="5" color={color}>
          {name}
        </Heading>
        <Text size="2" color={color || 'gray'}>
          {`${points} point${points !== 1 ? 's' : ''}`}
        </Text>
      </Flex>

      <RadixMarkdown>
        {body}
      </RadixMarkdown>

      <Flex direction="row" gap="2" align="center" justify="between">
        <Text size="2" color={color || 'gray'}>
          {startCase(status)}
        </Text>
        {status !== 'correct' && (
          <Text size="2" color={color || 'gray'}>
            {`${attemptsRemaining} attempt${attemptsRemaining !== 1 ? 's' : ''} left`}
          </Text>
        )}
      </Flex>

      <Form.Root onSubmitCapture={handleSubmit}>
        <Flex direction="row" gap="2" align="start">
          <Form.Field name="flag" className="grow">
            <Form.Control asChild>
              <TextField.Root
                className={twMerge(
                  'ss02',
                  status !== 'unanswered' && '!ring ring-(--accent-a7)',
                )}
                color={color || COLOR_QUESTION}
                placeholder={placeholder}
                required
                autoComplete="off"
                disabled={status === 'correct' || attemptsRemaining <= 0 || denied}
              >
                <TextField.Slot>
                  <TbFlag2 className={twMerge(status !== 'unanswered' && 'text-(--accent-10)')} />
                </TextField.Slot>
              </TextField.Root>
            </Form.Control>
            <Form.Message match="valueMissing">Flag cannot be empty</Form.Message>
          </Form.Field>

          <RequireEventPermission eventId={eventId} permission="CAN_PLAY_CHALLENGES" permissionDeniedPlaceholder={null}>
            {status !== 'correct' && attemptsRemaining > 0 && (
            <Button variant="soft" size="2" type="submit" color={color || COLOR_QUESTION}>
              Submit
            </Button>
            )}
          </RequireEventPermission>
        </Flex>
      </Form.Root>

    </Flex>
  );
}
