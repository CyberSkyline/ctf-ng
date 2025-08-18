import { COLOR_HINT } from '@/constants';
import { useContainerLogs } from '@/hooks/container';
import { Button, Code, Skeleton } from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import Modal from 'components/Modal';
import { useEffect, useRef } from 'react';
import { TbScript } from 'react-icons/tb';

function ContainerLog({ containerId }: { containerId: number }) {
  const { data, error } = useContainerLogs(containerId);
  const logContainerRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current!.scrollTop = logContainerRef.current!.scrollHeight;
    }
  }, [ data ]);

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  return (
    <Skeleton loading={!data}>
      <Code color="gray" className="!whitespace-pre !block !p-2 !h-96 overflow-auto !w-[80ch] !box-content" ref={logContainerRef}>
        {data}
      </Code>
    </Skeleton>
  );
}

export default function ContainerLogsModal({ containerId }: { containerId: number }) {
  return (
    <Modal
      title="Container Logs"
      trigger={(
        <Button
          variant="ghost"
          color={COLOR_HINT}
          className="!mx-0"
        >
          <TbScript />
          Logs
        </Button>
        )}
      className="!max-w-fit"
    >
      <ContainerLog containerId={containerId} />
    </Modal>
  );
}
