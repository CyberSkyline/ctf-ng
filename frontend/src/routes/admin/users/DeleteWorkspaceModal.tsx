import { COLOR_NEGATIVE } from '@/constants';
import { deleteWorkspace } from '@/hooks/users';
import { Button, Text } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbTrash } from 'react-icons/tb';
import { WarningCallout } from 'components/Callouts'

export default function DeleteWorkspaceModal({ userId }: {userId: number}) {
  return (
    <Modal
      title="Delete Workspace Container"
      description="Are you sure you want to delete this workspace?"
      submitVerb="Delete"
      submitColor={COLOR_NEGATIVE}
      onSubmit={async () => deleteWorkspace(userId)}
      trigger={(
        <Button
          variant="ghost"
          color={COLOR_NEGATIVE}
          className="!mx-0"
        >

          <TbTrash />
          Delete
        </Button>
      )}
    >
      <WarningCallout>
        This will result in lost data
      </WarningCallout>
      <Text color="gray">
        The workspace and its db object will be deleted. This will remove all ephemeral data stored in the workspace.
      </Text>
    </Modal>
  );
}
