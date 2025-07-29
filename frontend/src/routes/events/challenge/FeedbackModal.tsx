import { COLOR_INFO } from '@/constants';
import { Button } from '@radix-ui/themes';
import { WarningCallout } from 'components/Callouts';
import Modal from 'components/Modal';
import { TbSpeakerphone } from 'react-icons/tb';

export default function FeedbackModal() {
  return (
    <Modal
      title="Feedback"
      trigger={(
        <Button variant="ghost" color={COLOR_INFO} className="!m-0">
          <TbSpeakerphone />
          Feedback
        </Button>
    )}
    >
      <WarningCallout>
        Not yet implemented.
      </WarningCallout>
    </Modal>
  );
}
