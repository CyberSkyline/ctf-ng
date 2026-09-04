import {
  COLOR_INFO,
  COLOR_POSITIVE,
  COLOR_WARNING,
  type AccentColor,
} from '@/constants';
import { Badge } from '@radix-ui/themes';
import type { Responsive } from '@radix-ui/themes/props';

const TYPES: {[key: string]: {label: string, color: AccentColor}} = {
  general : { label : 'General', color : 'gray' },
  event_update : { label : 'Event Update', color : COLOR_INFO },
  event_start : { label : 'Event Start', color : COLOR_POSITIVE },
  event_end : { label : 'Event End', color : COLOR_WARNING },
  leaderboard_update : { label : 'Leaderboard Update', color : COLOR_INFO },
};

export default function AnnouncementTypeBadge({ type, size = '1' }: { type: string, size?: Responsive<'1' | '2' | '3'> }) {
  const { label, color } = TYPES[type] ?? { label : type, color : 'gray' };

  return <Badge color={color} size={size}>{label}</Badge>;
}
