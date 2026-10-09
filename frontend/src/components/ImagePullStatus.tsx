import { COLOR_NEGATIVE, COLOR_POSITIVE } from '@/constants';
import { useDockerHosts, useImagePullStatus } from '@/hooks/container';
import {
  Code,
  Flex,
  HoverCard,
  Progress,
  Skeleton,
  Text,
} from '@radix-ui/themes';
import { TbCancel, TbCheck } from 'react-icons/tb';

function HostPullStatus({ id, host } : { id: string | number, host: string }) {
  const { data : pull } = useImagePullStatus(id, host);

  if (pull?.status === 'fail') {
    return (
      <Flex direction="row" align="center" gap="2">
        <Text size="2" color="gray">{host}</Text>
        <HoverCard.Root>
          <HoverCard.Trigger>
            <button type="button" aria-label="Show error details">
              <Text color={COLOR_NEGATIVE} className="underline decoration-dashed">
                <TbCancel className="inline me-1" />
                Error
              </Text>
            </button>
          </HoverCard.Trigger>
          <HoverCard.Content>
            <Code color="gray" className="block whitespace-pre-wrap">{pull.error}</Code>
          </HoverCard.Content>
        </HoverCard.Root>
      </Flex>
    );
  }

  return (
    <Flex direction="row" align="center" gap="2">
      <Text size="2" color="gray">{host}</Text>
      {pull?.status === 'success' && (
      <Text color={COLOR_POSITIVE}>
        <TbCheck className="inline me-1" />
        Pulled
      </Text>
      )}
      {pull?.status === 'pulling' && (
      <>
        {!!pull.percent && (
        <Text size="2" color="gray">Pulling</Text>
        )}
        <Skeleton loading={!pull.percent}>
          <Progress value={pull.percent} className="w-24" />
        </Skeleton>
      </>
      )}
    </Flex>
  );
}

export default function ImagePullStatus({ id } : { id: string | number }) {
  const { data : hosts } = useDockerHosts();

  if (!hosts?.length) {
    return null;
  }

  return (
    <Flex direction="column" gap="1">
      {hosts.map((host) => <HostPullStatus key={host} id={id} host={host} />)}
    </Flex>
  );
}
