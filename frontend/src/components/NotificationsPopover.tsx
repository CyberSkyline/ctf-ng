import {
  Button,
  Card,
  Flex,
  Text,
} from '@radix-ui/themes';
import { NavigationMenu } from 'radix-ui';
import { ErrorCallout } from 'components/Callouts';
import {
  markAllNotificationsRead,
  markNotificationRead,
  useMyNotifications,
  useUnreadCount,
} from '@/hooks/notifications';
import { useNavigate } from 'react-router';
import { isUndefined, map, includes } from 'lodash';
import { TbNotification, TbCircleDotFilled, TbBell } from 'react-icons/tb';
import { useState } from 'react';
import { twMerge } from 'tailwind-merge';
import { NOTIF_TYPE } from '@/constants';

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
        tabIndex="0"
        key={notif.id}
        onKeyDown={(event) => {
          if (event.key === 'Enter') {
            markRead(link, notif.id);
          }
        }}
        onClick={() => markRead(link, notif.id)}
        className="hover:border-b-2"
      >
        <Flex justify="between">
          <Text weight={notif.read_at ? 'regular' : 'bold'}>{notif.title}</Text>
          <Text>{notif.created_at.toLocaleDateString('en-US', dateFormat)}</Text>
        </Flex>
        <Text size="2">{notif.message}</Text>
      </Card>
    );
  };

  return (
    <NavigationMenu.Item value="temp">
      <NavigationMenu.Trigger
        className={twMerge(triggerClassName, 'h-full', unreadCount?.count !== 0 && 'pb-4')}
        onPointerMove={(event) => event.preventDefault()}
        onPointerLeave={(event) => event.preventDefault()}
      >
        <TbBell />
        {unreadCount?.count !== 0 && <TbCircleDotFilled color="var(--accent-indicator)" className="-mt-6 ml-3" />}
      </NavigationMenu.Trigger>
      <NavigationMenu.Content
        className={twMerge(contentClassName, 'p-4')}
        onPointerEnter={(event) => event.preventDefault()}
        onPointerLeave={(event) => event.preventDefault()}
      >
        {isUndefined(data) ? (
          <Flex
            direction="column"
            align="center"
            justify="center"
            width="300px"
            height="300px"
          >
            <TbNotification size={32} />
            {error ? <ErrorCallout>{error}</ErrorCallout> : <Text weight="bold">No Notifications</Text>}
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
