import {
  COLOR_INFO,
  COLOR_NEGATIVE,
  COLOR_POSITIVE,
  COLOR_WARNING,
  type AccentColor,
} from '@/constants';
import { useEventStatus } from '@/hooks/events';
import { useEventPermission } from '@/hooks/permissions';
import { useRegistration } from '@/hooks/users';
import { Badge, Skeleton } from '@radix-ui/themes';
import type { Responsive } from '@radix-ui/themes/props';
import type { IconType } from 'react-icons';
import {
  TbArrowRight,
  TbCheck,
  TbClock,
  TbPlayerPlay,
  TbUsersPlus,
} from 'react-icons/tb';

/** Maps an event state onto label, color, and icon to display in the UI. */
const EVENT_STATES: {
    [key: string]: {
        color: AccentColor;
        label: string;
        icon: IconType;
    };
} = {
  registration_open : {
    color : COLOR_INFO,
    label : 'Registration Open',
    icon : TbArrowRight,
  },
  registered : {
    color : COLOR_POSITIVE,
    label : 'Registered',
    icon : TbCheck,
  },
  invalid : {
    color : COLOR_NEGATIVE,
    label : 'More Members Required',
    icon : TbUsersPlus,
  },
  ready : {
    color : COLOR_INFO,
    label : 'Ready to Start',
    icon : TbClock,
  },
  waiting : {
    color : COLOR_WARNING,
    label : 'Waiting for Captain',
    icon : TbClock,
  },
  playing : {
    color : COLOR_POSITIVE,
    label : 'Playing',
    icon : TbPlayerPlay,
  },
  live : {
    color : COLOR_POSITIVE,
    label : 'Happening Now',
    icon : TbPlayerPlay,
  },
  participated : {
    color : COLOR_NEGATIVE,
    label : 'Time Up',
    icon : TbClock,
  },
  ended : {
    color : 'gray',
    label : 'Ended',
    icon : TbCheck,
  },
};

export default function EventBadge({ eventId, size, className }: { eventId: number; size?: Responsive<'1' | '2' | '3'>; className?: string }) {
  const {
    isRegistered, isStarted, isFinished, team, isLoading,
  } = useRegistration(eventId);
  const {
    isRegistrationOpen, isOngoing, isConcluded, isLoading : statusLoading, event,
  } = useEventStatus(eventId);
  const { granted, isLoading : permissionLoading } = useEventPermission('CAN_START_TEAM_TIMER', isRegistered ? eventId : null);

  let state;

  if (isLoading || statusLoading || permissionLoading) {
    return <Skeleton><Badge size={size} className={className}>Loading...</Badge></Skeleton>;
  }

  if (isOngoing) {
    state = 'live';
  }

  if (isRegistrationOpen) {
    state = 'registration_open';
  }

  if (isRegistered) {
    state = 'registered';

    if (isOngoing && !isStarted) {
      state = granted ? 'ready' : 'waiting';
    }

    if (team!.member_count === 1 && event!.max_team_size > 1) {
      state = 'invalid';
    }

    if (isOngoing && isStarted) {
      state = 'playing';
    }

    if (isFinished) {
      state = 'participated';
    }
  }

  if (isConcluded) {
    state = 'ended';
  }

  if (!state) {
    return null;
  }

  const { color, label, icon : Icon } = EVENT_STATES[state];

  return (
    <Badge color={color} variant="soft" size={size} className={className} role="status">
      {Icon && <Icon className="inline" />}
      {label}
    </Badge>
  );
}
