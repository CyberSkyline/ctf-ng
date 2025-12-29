import { COLOR_INFO } from '@/constants';
import { connectDeployment } from '@/hooks/container';
import { Button, Text } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbNetwork } from 'react-icons/tb';

export default function ConnectDeploymentModal({ challengeId, teamId }: {challengeId: number, teamId : number}) {
  return (
    <Modal
      title="Connect to Deployment networks"
      description="This will connect your workstation to all the networks in this deployment"
      submitVerb="Connect"
      submitColor={COLOR_INFO}
      onSubmit={async () => connectDeployment(challengeId, teamId)}
      trigger={(
        <Button
          variant="soft"
          color={COLOR_INFO}
        >
          <TbNetwork />
          Connect
        </Button>
      )}
    >
      <Text color="gray">
        This will disconnect your workspace from any networks it is currently attached to.
        Then it will attach you to all networks used in this deployment. Including networks hidden from the player.
      </Text>
    </Modal>
  );
}
