import { NOTIF_TYPE } from '@/constants';
import {
  markAllNotificationsRead,
  markNotificationRead,
  useMyNotifications,
  useUnreadCount,
} from '@/hooks/notifications';
import type { Notification } from '@/types';
import {
  Button,
  Card,
  Flex,
  Text,
} from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import {
  includes,
  isEmpty,
  isUndefined,
  map,
} from 'lodash';
import { NavigationMenu } from 'radix-ui';
import { useState } from 'react';
import { TbBell, TbCircleDotFilled, TbNotification } from 'react-icons/tb';
import { useNavigate } from 'react-router';
import { twMerge } from 'tailwind-merge';

export default function NotificationsPopover({ triggerClassName, contentClassName }: { triggerClassName?: string, contentClassName?: string }) {
  const { data, error } = useMyNotifications();
  const { data : unreadCount } = useUnreadCount();
  const navigate = useNavigate();
  const [ readError, setReadError ] = useState(null);

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

  const markRead = (link: string, id: number) => {
    markNotificationRead(id)
      .catch((err) => setReadError(err.message))
      .finally(() => navigate(link));
  };

  const getCard = (notif: Notification) => {
    let link = '';
    if (includes(TICKETS, notif.type)) {
      link = `/support/${notif.ticket_id}`;
    } // keep structure in place for future possible expansions of notif_types

    return (
      <Card
        tabIndex={0}
        key={notif.id}
        onKeyDown={(event) => {
          if (event.key === 'Enter') {
            markRead(link, notif.id);
          }
        }}
        onClick={() => markRead(link, notif.id)}
        className="hover:border-b-2 w-xs"
      >
        <Flex direction="column">
          <Text weight={notif.read_at ? 'regular' : 'bold'}>{notif.title}</Text>
          <Text size="1">{notif.created_at.toLocaleDateString('en-US', dateFormat)}</Text>
          <Text size="2" wrap="pretty" className="pt-2">{notif.message}</Text>
        </Flex>
      </Card>
    );
  };

  return (
    <NavigationMenu.Item value="temp">
      <NavigationMenu.Trigger
        className={twMerge(triggerClassName, 'h-full')}
        onPointerMove={(event) => event.preventDefault()}
        onPointerLeave={(event) => event.preventDefault()}
      >
        <TbBell aria-label="Notifications" />
        {unreadCount && unreadCount.count > 0
          && <TbCircleDotFilled color="var(--accent-indicator)" className="absolute -mt-6 ml-2" aria-label="Unread" />}
      </NavigationMenu.Trigger>
      <NavigationMenu.Content
        className={twMerge(contentClassName, 'p-4')}
        onPointerEnter={(event) => event.preventDefault()}
        onPointerLeave={(event) => event.preventDefault()}
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
            {readError && <ErrorCallout className="mb-3">{readError}</ErrorCallout>}
            {map(data, (notif) => getCard(notif))}
          </Flex>
        )}
      </NavigationMenu.Content>
    </NavigationMenu.Item>
  );
}
