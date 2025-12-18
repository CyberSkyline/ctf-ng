import { COLOR_NEGATIVE } from '@/constants';
import { recycleWorkspace } from '@/hooks/users';
import { Button, Strong } from '@radix-ui/themes';
import { WarningCallout } from 'components/Callouts';
import Modal from 'components/Modal';
import { TbRecycle } from 'react-icons/tb';

export default function RecycleWorkspaceModal({ userId }: {userId: number}) {
  return (
    <Modal
      title="Recycle Workspace"
      description="Are you sure you want to recycle this workspace?"
      submitVerb="Recycle"
      submitColor={COLOR_NEGATIVE}
      onSubmit={async () => recycleWorkspace(userId)}
      trigger={(
        <Button
          variant="ghost"
          color={COLOR_NEGATIVE}
        >
          <TbRecycle />
          Recycle
        </Button>
      )}
    >
      <WarningCallout>
        The workspace will be deleted and recreated from scratch.
        <br />
        <Strong>Any user data and configuration inside this workspace will be lost.</Strong>
      </WarningCallout>
    </Modal>
  );
}
