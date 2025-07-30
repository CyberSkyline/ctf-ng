import {
  Box,
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

import { useCallback, useMemo } from 'react';

export default function ChallengeQuestion({
  name,
  question,
  placeholder,
  points,
  attemptsRemaining,
  status,
  valueOverride,
}: {
  name: string;
  question: string;
  placeholder: string;
  points: number;
  attemptsRemaining: number;
  status: 'unanswered' | 'incorrect' | 'correct';
  valueOverride?: string;
}) {
  const handleSubmit = useCallback((event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const { flag } = Object.fromEntries(new FormData(event.currentTarget));

    alert(flag);
  }, []);

  const color = useMemo(() => {
    switch (status) {
      case 'incorrect':
        return 'red';
      case 'correct':
        return 'lime';
      default:
        return 'amber';
    }
  }, [ status ]);

  return (
    <Flex direction="column">
      <Flex direction="row" gap="2" align="center" justify="start">
        <Heading size="5" color={status === 'correct' ? 'lime' : undefined}>
          {name}
        </Heading>
        <Text size="2" color={status === 'correct' ? 'lime' : 'gray'}>
          {points}
          {' '}
          points
        </Text>
      </Flex>

      <RadixMarkdown>
        {question}
      </RadixMarkdown>

      <Flex direction="row" gap="2" align="center" justify="between">
        <Box>
          {status === 'correct' && (
            <Text size="2" color="lime">
              Correct
            </Text>
          )}
          {status === 'incorrect' && (
            <Text size="2" color="red">
              Incorrect
            </Text>
          )}
          {status === 'unanswered' && (
            <Text size="2" color="gray">
              Unanswered
            </Text>
          )}
        </Box>
        <Text size="2" color="gray">
          {`${attemptsRemaining} attempt${attemptsRemaining !== 1 ? 's' : ''} left`}
        </Text>
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
                color={color}
                placeholder={placeholder}
                required
                defaultValue={valueOverride}
                disabled={status === 'correct' || attemptsRemaining <= 0}
              >
                <TextField.Slot>
                  <TbFlag2 className={twMerge(status !== 'unanswered' && 'text-(--accent-10)')} />
                </TextField.Slot>
              </TextField.Root>
            </Form.Control>
            <Form.Message match="valueMissing">Flag cannot be empty</Form.Message>
          </Form.Field>

          {status !== 'correct' && attemptsRemaining > 0 && (
            <Button variant="soft" size="2" type="submit" color="amber">
              Submit
            </Button>
          )}
        </Flex>
      </Form.Root>

    </Flex>
  );
}
