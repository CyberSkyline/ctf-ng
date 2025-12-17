import { COLOR_NEGATIVE } from '@/constants';
import { recycleDeployment } from '@/hooks/container';
import { Button, Text } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbRecycle } from 'react-icons/tb';

export default function RecycleDeploymentModal({ challengeId, teamId }: {challengeId: number, teamId : number}) {
  return (
    <Modal
      title="Recycle Deployment"
      description="Are you sure you want to recycle this deployment?"
      submitVerb="Recycle"
      submitColor={COLOR_NEGATIVE}
      onSubmit={async () => recycleDeployment(challengeId, teamId)}
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
      <Text color="gray">
        The whole deployment will be deleted and recreated from scratch. This will remove all ephemeral data stored in the container.
      </Text>
    </Modal>
  );
}
