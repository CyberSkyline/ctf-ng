import {
  COLOR_INFO,
  COLOR_POSITIVE,
  COLOR_WARNING,
  type AccentColor,
} from '@/constants';
import { Badge } from '@radix-ui/themes';
import type { IconType } from 'react-icons';
import { TbCheck, TbClock, TbPlayerPlayFilled } from 'react-icons/tb';

/** Maps an event state onto label, color, and icon to display in the UI. */
const EVENT_STATES: {
    [key: string]: {
        color: AccentColor;
        label: string;
        icon: IconType;
    };
} = {
  upcoming : {
    color : COLOR_INFO,
    label : 'Upcoming',
    icon : TbClock,
  },
  waiting : {
    color : COLOR_WARNING,
    label : 'Waiting for team',
    icon : TbClock,
  },
  live : {
    color : COLOR_POSITIVE,
    label : 'Happening Now',
    icon : TbPlayerPlayFilled,
  },
  ended : {
    color : 'gray',
    label : 'Ended',
    icon : TbCheck,
  },
};

export default function EventBadge({ state }: { state: 'upcoming' | 'waiting' | 'live' | 'ended' }) {
  const { color, label, icon : Icon } = EVENT_STATES[state];
  return (
    <Badge color={color} variant="soft" size="3">
      {Icon && <Icon className="inline" />}
      {label}
    </Badge>
  );
}
