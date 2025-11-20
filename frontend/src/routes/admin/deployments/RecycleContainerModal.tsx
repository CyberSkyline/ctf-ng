import { COLOR_NEGATIVE } from '@/constants';
import { recycleContainer, useContainerStatus } from '@/hooks/container';
import { Button, Text } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbRecycle } from 'react-icons/tb';

export default function RecycleContainerModal({ containerId }: {containerId: number}) {
  const { data : status } = useContainerStatus(containerId);

  return (
    <Modal
      title="Recycle Container"
      description={`Are you sure you want to recycle ${status?.name || 'this container'}?`}
      submitVerb="Recycle"
      submitColor={COLOR_NEGATIVE}
      onSubmit={async () => recycleContainer(containerId)}
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
        The container will be deleted and recreated from scratch. This will remove all ephemeral data stored in the container.
      </Text>
    </Modal>
  );
}
