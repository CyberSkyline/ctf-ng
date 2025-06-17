import {
  Badge, Box, Flex, Heading, Text, Tooltip,
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
}: {
    label: string;
    value: string | number;
    description?: string;
    delta?: string;
}) {
  const deltaColor = delta && delta.startsWith('-') ? 'red' : 'green';

  return (
    <Box>
      <Flex direction="row" align="center" gap="1">
        <Text color="gray" size="2">{label}</Text>
        {description && (
        <Tooltip content={description}>
          <Text color="gray"><TbInfoCircle /></Text>
        </Tooltip>
        )}
        {delta && <Badge color={deltaColor} variant="soft" radius="full">{delta}</Badge> }
      </Flex>
      <Heading size="8" className="tabular-nums">{value}</Heading>
    </Box>
  );
}
