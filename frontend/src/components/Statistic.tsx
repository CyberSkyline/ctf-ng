import { COLOR_NEGATIVE, COLOR_POSITIVE } from '@/constants';
import {
  Badge,
  Box,
  Flex,
  Heading,
  Text,
  Tooltip,
} from '@radix-ui/themes';
import { TbInfoCircle } from 'react-icons/tb';

/**
 * Displays an emphasized statistic with an optional label,
 * description (accessible via hover), and delta.
 *
 * Combine multiple in a Flex or Grid component for more complex layouts.
 */
export default function Statistic({
  label,
  value,
  description = undefined,
  delta = undefined,
  size = '8',
}: {
  label: string;
  value: string | number;
  description?: string;
  delta?: string;
  size?: React.ComponentProps<typeof Heading>['size'],
}) {
  const deltaColor = delta && delta.startsWith('-') ? COLOR_NEGATIVE : COLOR_POSITIVE;

  return (
    <Box>
      <Flex direction="row" align="center" gap="1">
        <Text color="gray" size="2">{label}</Text>
        {description && (
          <Tooltip content={description}>
            <button type="button">
              <Text color="gray">
                <TbInfoCircle aria-label="More info" />
              </Text>
            </button>
          </Tooltip>
        )}
        {delta && <Badge color={deltaColor} variant="soft" radius="full">{delta}</Badge> }
      </Flex>
      <Heading size={size} asChild className="tabular-nums"><span>{value}</span></Heading>
    </Box>
  );
}
