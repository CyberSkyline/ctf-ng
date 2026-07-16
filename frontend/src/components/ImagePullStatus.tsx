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
import { TbCancel, TbCheck } from 'react-icons/tb';

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
    );
  }

  return null;
}
