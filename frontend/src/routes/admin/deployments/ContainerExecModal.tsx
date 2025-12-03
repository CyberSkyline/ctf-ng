import { COLOR_HINT } from '@/constants';
import { Button } from '@radix-ui/themes';
import Modal from 'components/Modal';
import Terminal from 'components/Terminal';
import { TbTerminal } from 'react-icons/tb';

export default function ContainerExecModal({ containerId }: {containerId: number}) {
  return (
    <Modal
      title="Container Terminal"
      trigger={(
        <Button variant="ghost" color={COLOR_HINT}>
          <TbTerminal />
          Terminal
        </Button>
      )}
      className="!max-w-3xl"
    >
      <Terminal containerId={containerId} />
    </Modal>
  );
}
