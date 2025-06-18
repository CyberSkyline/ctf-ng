import { Badge } from '@radix-ui/themes';
import { TbCheck, TbClock, TbPlayerPlayFilled } from 'react-icons/tb';
import type { accentColors } from '@radix-ui/themes/props';
import type { IconType } from 'react-icons';

/** Maps an event state onto label, color, and icon to display in the UI. */
const EVENT_STATES: {
    [key: string]: {
        color: typeof accentColors[number];
        label: string;
        icon: IconType;
    };
} = {
  upcoming: {
    color: 'blue',
    label: 'Upcoming',
    icon: TbClock,
  },
  waiting: {
    color: 'yellow',
    label: 'Waiting for team',
    icon: TbClock,
  },
  live: {
    color: 'lime',
    label: 'Happening Now',
    icon: TbPlayerPlayFilled,
  },
  ended: {
    color: 'gray',
    label: 'Ended',
    icon: TbCheck,
  },
};

export default function EventBadge({ state }: { state: 'upcoming' | 'waiting' | 'live' | 'ended' }) {
  const { color, label, icon: Icon } = EVENT_STATES[state];
  return (
    <Badge color={color} variant="soft" size="3">
      {Icon && <Icon className="inline" />}
      {label}
    </Badge>
  );
}
