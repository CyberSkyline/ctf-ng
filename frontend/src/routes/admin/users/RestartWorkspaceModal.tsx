import { COLOR_WARNING } from '@/constants';
import { restartWorkspace } from '@/hooks/users';
import { Button, Text } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbReload } from 'react-icons/tb';

export default function RestartWorkspaceModal({ userId }: {userId: number}) {
  return (
    <Modal
      title="Restart Container"
      description="Are you sure you want to restart this workspace?"
      submitVerb="Restart"
      submitColor={COLOR_WARNING}
      onSubmit={async () => restartWorkspace(userId)}
      trigger={(
        <Button
          variant="ghost"
          color={COLOR_WARNING}
          className="!mx-0"
        >
          <TbReload />
          Restart
        </Button>
      )}
    >
      <Text color="gray">
        The Workspace may be unavailable for a short period during the restart.
      </Text>
    </Modal>
  );
}
