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
import { useEffect, useRef, useState } from 'react';
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

export default function EventBadge({
  eventId, size, className, announce = false,
}: {
  eventId: number;
  size?: Responsive<'1' | '2' | '3'>;
  className?: string;
  /**
   * Announce status changes that happen while the page is open (registering, the captain starting the timer,
   * team changes) via a hidden live region (WCAG 4.1.3). The first status shown is never announced, so page
   * loads stay quiet. Use on the event page header only, not on cards in a list.
   */
  announce?: boolean;
}) {
  const {
    isRegistered, isStarted, isFinished, team, isLoading,
  } = useRegistration(eventId);
  const {
    isRegistrationOpen, isOngoing, isConcluded, isLoading : statusLoading, event,
  } = useEventStatus(eventId);
  const { granted, isLoading : permissionLoading } = useEventPermission('CAN_START_TEAM_TIMER', isRegistered ? eventId : null);

  const loading = isLoading || statusLoading || permissionLoading;
  let state: string | undefined;

  // practice events don't display status badges
  if (!loading && !event?.practice) {
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
  }

  const label = state ? EVENT_STATES[state].label : null;

  // Announce only changes after the first resolved status for this event.
  const [ announcement, setAnnouncement ] = useState('');
  const lastSeen = useRef<{ eventId: number, label: string | null } | null>(null);

  useEffect(() => {
    if (!announce || loading) return;

    const previous = lastSeen.current;
    if (previous && previous.eventId !== eventId) {
      // Moved to another event: drop the old event's text, so a later change on this event to the same
      // wording still changes the region's content and is announced.
      setAnnouncement('');
    } else if (previous && previous.label !== label && label) {
      setAnnouncement(`Event status: ${label}`);
    }
    lastSeen.current = { eventId, label };
  }, [ announce, loading, eventId, label ]);

  let badge = null;

  if (loading) {
    badge = <Skeleton><Badge size={size} className={className}>Loading...</Badge></Skeleton>;
  } else if (state) {
    const { color, icon : Icon } = EVENT_STATES[state];

    badge = (
      <Badge color={color} variant="soft" size={size} className={className}>
        {Icon && <Icon className="inline" />}
        {label}
      </Badge>
    );
  }

  return (
    <>
      {/* Mounted before any change so screen readers pick up updates to its text. */}
      {announce && <span className="sr-only" role="status">{announcement}</span>}
      {badge}
    </>
  );
}
