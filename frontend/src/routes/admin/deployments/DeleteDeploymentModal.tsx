import { COLOR_NEGATIVE } from '@/constants';
import { deleteDeployment } from '@/hooks/container';
import { Button, Text } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbTrash } from 'react-icons/tb';
import { WarningCallout } from 'components/Callouts'

export default function DeleteDeploymentModal({ challengeId, teamId }: {challengeId: number, teamId : number}) {
  return (
    <Modal
      title="Delete Deployment"
      description="Are you sure you want to delete this deployment?"
      submitVerb="Delete"
      submitColor={COLOR_NEGATIVE}
      onSubmit={async () => deleteDeployment(challengeId, teamId)}
      trigger={(
        <Button
          variant="soft"
          color={COLOR_NEGATIVE}
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
        The whole deployment will be deleted, containers and associated database records, will be permently gone.
      </Text>
    </Modal>
  );
}
