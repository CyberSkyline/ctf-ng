import { COLOR_POSITIVE } from '@/constants';
import { pullVNCImage } from '@/hooks/container';
import { Button, Text } from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import Modal from 'components/Modal';
import socket from '@/socket';
import { TbDownload } from 'react-icons/tb';
import { useEffect, useState } from 'react';

type Status = 'pulling' | 'success' | 'fail' | null;

export default function AdminPullVncModal() {
  const [ pullState, setPullState ] = useState<Status>(null);
  const [ pullError, setPullError ] = useState<string>();

  const handlePull = async () => {
    setPullState('pulling');
    pullVNCImage();
  };

  useEffect(() => {
    socket.on('pull-success', () => {
      setPullState('success');
    });

    socket.on('pull-fail', ({ error } : { error: string }) => {
      setPullState('fail');
      setPullError(error);
    });
  }, []);

  const buttonMessage = pullState ? 'Image Pull Succes' : 'Pull Vnc Image';

  if (pullError) {
    return (
      <ErrorCallout className="ml-4">
        {pullError}
      </ErrorCallout>
    );
  }

  return (
    <Modal
      title="Pull VNC Container image"
      description="This will pull the VNC container image."
      submitVerb="Pull"
      submitColor={COLOR_POSITIVE}
      onSubmit={handlePull}
      trigger={(
        <Button
          color={COLOR_POSITIVE}
          loading={pullState === 'pulling'}
        >
          <TbDownload />
          {buttonMessage}
        </Button>
      )}
    >
      <Text color="gray">
        The workspace VNC will be pulled. All existing workspaces will need to be recycled to get the new image.
      </Text>
    </Modal>
  );
}
