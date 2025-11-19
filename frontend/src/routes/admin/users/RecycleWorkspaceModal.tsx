import { COLOR_NEGATIVE } from '@/constants';
import { recycleWorkspace } from '@/hooks/users';
import { Button, Text } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbRecycle } from 'react-icons/tb';

export default function RecycleWorkspaceModal({ userId }: {userId: number}) {
  return (
    <Modal
      title="Recycle Container"
      description="Are you sure you want to recycle this workspace?"
      submitVerb="Recycle"
      submitColor={COLOR_NEGATIVE}
      onSubmit={async () => recycleWorkspace(userId)}
      trigger={(
        <Button
          variant="ghost"
          color={COLOR_NEGATIVE}
          className="!mx-0"
        >
          <TbRecycle />
          Recycle
        </Button>
      )}
    >
      <Text color="gray">
        The workspace will be deleted and recreated from scratch. This will remove all ephemeral data stored in the workspace.
      </Text>
    </Modal>
  );
}
