import { COLOR_NEGATIVE, NOTIF_TYPE } from '@/constants';
import {
  markAllNotificationsRead,
  markNotificationRead,
  useMyNotifications,
  useNotificationSoundEnabled,
  useUnreadCount,
} from '@/hooks/notifications';
import type { Notification } from '@/types';
import { formatDate } from '@/util';
import {
  Button,
  Card,
  Flex,
  Text,
} from '@radix-ui/themes';
import ding from 'assets/audio/ding.mp3';
import { ErrorCallout } from 'components/Callouts';
import RadixMarkdown from 'components/RadixMarkdown';
import {
  includes,
  isEmpty,
  isNil,
  isUndefined,
  map,
} from 'lodash';
import { NavigationMenu } from 'radix-ui';
import { useEffect, useRef, useState } from 'react';
import { TbBell, TbCircleDotFilled, TbNotification } from 'react-icons/tb';
import { Link, useNavigate } from 'react-router';
import { twMerge } from 'tailwind-merge';

export default function NotificationsPopover({ itemClassName, triggerClassName, contentClassName }: {
  itemClassName?: string,
  triggerClassName?: string,
  contentClassName?: string,
}) {
  const { data, error } = useMyNotifications();
  const { data : unreadCount } = useUnreadCount();
  const navigate = useNavigate();
  const [ readError, setReadError ] = useState(null);
  const [ soundEnabled ] = useNotificationSoundEnabled();

  const previousUnreadCount = useRef<number | undefined>(undefined);
  const audioRef = useRef<HTMLAudioElement>(new Audio(ding));

  useEffect(() => {
    const count = unreadCount?.count;

    if (isNil(count)) return;

    // Play the notification sound if the unread count has increased
    // Only play the sound if the user localstorage setting for notification sound is enabled
    if (!isUndefined(previousUnreadCount.current) && count > previousUnreadCount.current && soundEnabled === true) {
      audioRef.current.currentTime = 0;
      audioRef.current.play().catch(() => {
        // throw away the error intentionally
      });
    }

    previousUnreadCount.current = count;
  }, [ unreadCount, soundEnabled ]);

  const dateFormat: Intl.DateTimeFormatOptions = {
    month : 'numeric',
    day : 'numeric',
    year : 'numeric',
  };

  const { TICKETS } = NOTIF_TYPE;

  const markAllRead = () => {
    markAllNotificationsRead()
      .catch((err) => setReadError(err.message));
  };

  // Used by the title control, which handles its own navigation (if any).
  const markReadInPlace = (id: number) => {
    markNotificationRead(id)
      .catch((err) => setReadError(err.message));
  };

  const markRead = (link: string, id: number) => {
    markNotificationRead(id)
      .catch((err) => setReadError(err.message))
      .finally(() => {
        if (link) navigate(link);
      });
  };

  const getCard = (notif: Notification) => {
    // The server picks the target for the recipient's role (admins get the admin ticket view, participants their
    // own ticket). Fall back to the participant ticket page for responses that predate the link field.
    let link = notif.link ?? '';
    if (!link && includes(TICKETS, notif.type) && !isNil(notif.ticket_id)) {
      link = `/support/${notif.ticket_id}`;
    }

    const unread = !notif.read_at;
    const messageId = `notification-${notif.id}-message`;
    const title = (
      <>
        {/* Unread is otherwise shown only by font weight. */}
        {unread && <span className="sr-only">Unread: </span>}
        {notif.title}
        {/*
          Many notifications share a title ("Support Ticket Update"), so add the ticket subject to the name to keep
          them distinguishable in a screen reader's links list (WCAG 2.4.4, 2.4.6).
        */}
        {notif.ticket_subject && <span className="sr-only">{`: ${notif.ticket_subject}`}</span>}
      </>
    );
    const titleClass = 'text-left hover:underline focus-visible:underline';

    // The title is the notification's control: a link when it opens something, otherwise a button that marks
    // it read. The card was a focusable div that handled only Enter and wrapped any links in the message
    // (WCAG 2.1.1, 4.1.2).
    return (
      <Card
        key={notif.id}
        // Mouse convenience: a click anywhere on the card acts like the title, except on links and buttons inside it.
        onClick={(event) => {
          if ((event.target as HTMLElement).closest('a, button')) return;
          markRead(link, notif.id);
        }}
        className="hover:border-b-2 w-xs max-sm:w-auto cursor-pointer"
      >
        <Flex direction="column">
          <Text weight={unread ? 'bold' : 'regular'}>
            {link ? (
              <NavigationMenu.Link asChild>
                <Link
                  to={link}
                  className={titleClass}
                  aria-describedby={messageId}
                  onClick={() => markReadInPlace(notif.id)}
                >
                  {title}
                </Link>
              </NavigationMenu.Link>
            ) : (
              <button
                type="button"
                className={titleClass}
                aria-describedby={messageId}
                onClick={() => markReadInPlace(notif.id)}
              >
                {title}
              </button>
            )}
          </Text>
          <Text size="1">{formatDate(notif.created_at, dateFormat)}</Text>
          {/* The control's description, so the message is read with it even when the subject is missing. */}
          <div id={messageId} className="pt-2 text-sm"><RadixMarkdown>{notif.message}</RadixMarkdown></div>
        </Flex>
      </Card>
    );
  };

  return (
    <NavigationMenu.Item value="temp" className={twMerge('relative', itemClassName)}>
      <NavigationMenu.Trigger
        className={twMerge(triggerClassName, 'h-full')}
        onPointerMove={(event) => event.preventDefault()}
        onPointerLeave={(event) => event.preventDefault()}
        aria-label={unreadCount && unreadCount.count > 0 ? `Notifications, ${unreadCount.count} unread` : 'Notifications'}
      >
        <TbBell aria-hidden="true" />
        {unreadCount && unreadCount.count > 0
          && <TbCircleDotFilled color={COLOR_NEGATIVE} className="absolute -mt-6 ml-2 pulsate" aria-hidden="true" />}
      </NavigationMenu.Trigger>
      <NavigationMenu.Content
        // On narrow screens the bell isn't at the right edge, so a panel aligned to it would run off the left
        // side of the viewport (WCAG 1.4.10). Span the viewport below the nav bar instead.
        className={twMerge(
          contentClassName,
          'max-h-86 overflow-y-auto overflow-x-hidden',
          'max-sm:fixed max-sm:inset-x-2 max-sm:top-(--NavBarHeight) max-sm:max-w-none',
        )}
      >
        {isUndefined(data) || isEmpty(data) ? (
          <Flex
            direction="column"
            align="center"
            justify="center"
            width="300px"
            height="300px"
          >
            <TbNotification size={32} />
            {error ? <ErrorCallout>{error.message}</ErrorCallout> : <Text weight="bold">No Notifications</Text>}
          </Flex>
        ) : (
          <Flex direction="column" className="gap-y-1">
            <Flex justify="end" className="pb-3">
              <Button
                size="1"
                onClick={markAllRead}
              >
                Mark All as Read
              </Button>
            </Flex>
            {readError && <ErrorCallout className="mb-3" announce>{readError}</ErrorCallout>}
            {map(data, (notif) => getCard(notif))}
          </Flex>
        )}
      </NavigationMenu.Content>
    </NavigationMenu.Item>
  );
}
