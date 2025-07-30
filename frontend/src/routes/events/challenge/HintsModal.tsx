import { useChallenge } from '@/hooks/challenge';
import { Button, Skeleton, Table } from '@radix-ui/themes';
import { ErrorCallout, WarningCallout } from 'components/Callouts';
import Modal from 'components/Modal';
import { TbBulb } from 'react-icons/tb';

export default function HintsModal({
  eventId, challengeId,
}: {
    eventId: number;
    challengeId: number;
}) {
  const { data, error } = useChallenge(eventId, challengeId);

  return (
    <Modal
      title="Hints"
      description="Hints can be redeemed in exchange for a deduction from your score."
      trigger={(
        <Button variant="ghost" color="purple" className="!m-0">
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
      <>
        <WarningCallout>Hint redemption is not yet implemented, enjoy your free hints for now!</WarningCallout>

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
              <Table.Row key={hint.id}>
                <Table.Cell>{hint.preview}</Table.Cell>
                <Table.Cell>
                  {hint.deduction}
                </Table.Cell>
                <Table.Cell>
                  <Skeleton loading={hint.body === null}>
                    {hint.body ?? 'Not redeemed'}
                  </Skeleton>
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table.Root>
      </>
      )}
    </Modal>
  );
}
