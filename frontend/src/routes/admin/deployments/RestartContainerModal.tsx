import { COLOR_WARNING } from '@/constants';
import { restartContainer, useContainerStatus } from '@/hooks/container';
import { Button, Text } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbReload } from 'react-icons/tb';

export default function RestartContainerModal({ containerId }: {containerId: number}) {
  const { data : status } = useContainerStatus(containerId);

  return (
    <Modal
      title="Restart Container"
      description={`Are you sure you want to restart ${status?.name || 'this container'}?`}
      submitVerb="Restart"
      submitColor={COLOR_WARNING}
      onSubmit={async () => restartContainer(containerId)}
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
        The container may be unavailable for a short period during the restart.
      </Text>
    </Modal>
  );
}
