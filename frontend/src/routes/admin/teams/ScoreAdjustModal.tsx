import { COLOR_WARNING } from '@/constants';
import { adjustPoints } from '@/hooks/team';
import type { Team } from '@/types';
import { Button, TextField } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { Form } from 'radix-ui';
import { TbPlusMinus } from 'react-icons/tb';

export default function ScoreAdjustModal({ team }: { team: Team }) {
  const handleSubmit = async (data: FormData) => {
    const { points, reason } = Object.fromEntries(data.entries());

    return adjustPoints(team.event_id, team.id, Number(points), reason as string);
  };

  return (
    <Modal
      title="Point Adjust"
      description={`Apply a manual score adjustment to ${team.name}.`}
      trigger={(
        <Button variant="soft" color={COLOR_WARNING}>
          <TbPlusMinus />
          Adjust Score
        </Button>
      )}
      onSubmit={handleSubmit}
      submitVerb="Adjust"
      submitColor={COLOR_WARNING}
    >
      <Form.Field name="points">
        <Form.Label>Adjustment</Form.Label>
        <Form.Control asChild>
          <TextField.Root type="number" placeholder="Number of points" required />
        </Form.Control>
        <Form.Message match="valueMissing" />
        <Form.Message match="badInput" />
      </Form.Field>
      <Form.Field name="reason">
        <Form.Label>Reason</Form.Label>
        <Form.Control asChild>
          <TextField.Root placeholder="Reason for adjustment" required />
        </Form.Control>
        <Form.Message match="valueMissing" />
      </Form.Field>
    </Modal>
  );
}
