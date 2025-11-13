import { COLOR_HINT } from '@/constants';
import { redeemHint, useChallenge } from '@/hooks/challenge';
import type { Hint } from '@/types';
import {
  Button,
  Flex,
  Popover,
  Table,
  Text,
} from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import Modal from 'components/Modal';
import { useState } from 'react';
import { TbBulb, TbLockOpen } from 'react-icons/tb';

function HintRow({ hint, eventId }: {hint: Hint, eventId: number}) {
  const [ loading, setLoading ] = useState(false);

  const handleRedeem = async () => {
    setLoading(true);
    return redeemHint(eventId, hint.challenge_id, hint.id).finally(() => {
      setLoading(false);
    });
  };

  return (
    <Table.Row key={hint.id}>
      <Table.Cell>{hint.preview}</Table.Cell>
      <Table.Cell>
        {hint.deduction}
      </Table.Cell>
      <Table.Cell align="right">
        {hint.body
          ? <Text>{hint.body}</Text>
          : (
            <Popover.Root>
              <Popover.Trigger>
                <Button variant="ghost" color={COLOR_HINT} type="button">
                  <TbLockOpen />
                  {' '}
                  Redeem
                </Button>
              </Popover.Trigger>
              <Popover.Content width="360px">
                <Text>
                  Are you sure you want to redeem
                  {' '}
                  {hint.preview}
                  ?
                </Text>
                <br />
                <Text color="gray" size="2">
                  This will deduct
                  {' '}
                  {hint.deduction}
                  {' '}
                  points from your score.
                </Text>

                <Flex direction="row" gap="2" mt="2" className="*:!grow">
                  <Popover.Close>
                    <Button variant="soft" color="gray">
                      Cancel
                    </Button>
                  </Popover.Close>
                  <Button variant="soft" color={COLOR_HINT} onClick={handleRedeem} loading={loading}>
                    Confirm
                  </Button>
                </Flex>
              </Popover.Content>
            </Popover.Root>
          )}
      </Table.Cell>
    </Table.Row>
  );
}

export default function HintsModal({
  challengeId,
}: {
    challengeId: number;
}) {
  const { data, error } = useChallenge(challengeId);

  return (
    <Modal
      title="Hints"
      description="Hints can be redeemed in exchange for a deduction from your score."
      trigger={(
        <Button variant="ghost" color={COLOR_HINT} className="!m-0">
          <TbBulb />
          Hints
        </Button>
      )}
    >
      {error && (
        <ErrorCallout>
          {error.message}
        </ErrorCallout>
      )}

      {data && (
        <Table.Root>
          <Table.Header>
            <Table.Row>
              <Table.ColumnHeaderCell>Hint</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Deduction</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell />
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {data?.hints.map((hint) => (
              <HintRow key={hint.id} hint={hint} eventId={eventId} />
            ))}
          </Table.Body>
        </Table.Root>
      )}
    </Modal>
  );
}
