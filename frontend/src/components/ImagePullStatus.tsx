import { COLOR_NEGATIVE, COLOR_POSITIVE } from '@/constants';
import { useImagePullStatus } from '@/hooks/container';
import {
  Code,
  Flex,
  HoverCard,
  Progress,
  Skeleton,
  Text,
} from '@radix-ui/themes';
import { TbCheck, TbInfoCircle } from 'react-icons/tb';

export default function ImagePullStatus({ id } : { id: string | number }) {
  const { data : pull } = useImagePullStatus(id);

  if (pull?.status === 'pulling') {
    return (
      <Flex direction="row" align="center" gap="2">
        {!!pull.percent && (
          <Text size="2" color="gray">Pulling</Text>
        )}
        <Skeleton loading={!pull.percent}>
          <Progress value={pull.percent} className="w-24" />
        </Skeleton>
      </Flex>
    );
  }

  if (pull?.status === 'success') {
    return (
      <Text color={COLOR_POSITIVE}>
        <TbCheck className="inline me-1" />
        Pulled
      </Text>
    );
  }

  if (pull?.status === 'fail') {
    return (
      <Flex direction="row" align="center" gap="1">
        <Text color={COLOR_NEGATIVE}>Error</Text>
        <HoverCard.Root>
          <HoverCard.Trigger>
            <button type="button">
              <Text color={COLOR_NEGATIVE}>
                <TbInfoCircle aria-label="More info" />
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

  return null;
}
