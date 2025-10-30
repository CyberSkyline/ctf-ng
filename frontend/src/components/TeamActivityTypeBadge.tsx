import {
  COLOR_HINT,
  COLOR_NEGATIVE,
  COLOR_POSITIVE,
  COLOR_WARNING,
  type AccentColor,
} from '@/constants';
import type { Attempt, HintRedemption, ManualPointAward } from '@/types';
import { Badge } from '@radix-ui/themes';

export default function TeamActivityTypeBadge({ data }: { data: Attempt | HintRedemption | ManualPointAward | undefined }) {
  if (!data) return undefined;

  let type = 'Unknown';
  let color: AccentColor = 'gray';

  if ('submission' in data) {
    type = (data as Attempt).is_correct ? 'Correct' : 'Incorrect';
    color = (data as Attempt).is_correct ? COLOR_POSITIVE : COLOR_NEGATIVE;
  }
  if ('hint_preview' in data) {
    type = 'Hint';
    color = COLOR_HINT;
  }
  if ('reason' in data) {
    type = 'Manual';
    color = COLOR_WARNING;
  }

  return (
    <Badge color={color}>
      {type.toUpperCase()}
    </Badge>
  );
}
