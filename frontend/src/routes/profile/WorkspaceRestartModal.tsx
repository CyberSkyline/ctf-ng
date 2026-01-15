import { COLOR_NEGATIVE } from '@/constants';
import { restartWorkspace } from '@/hooks/container';
import { Button, Text } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbReload } from 'react-icons/tb';

export default function WorkspaceRestartModal() {
  return (
    <Modal
      title="Restart Workspace"
      description=""
      submitVerb="Restart"
      submitColor={COLOR_NEGATIVE}
      onSubmit={async () => restartWorkspace()}
      trigger={(
        <Button
          color={COLOR_NEGATIVE}
        >
          <TbReload />
          Restart
        </Button>
      )}
    >
      <Text color="gray">
        This will restart your workspace. If you need your workspace completely reset please contact support.
      </Text>
    </Modal>
  );
}
