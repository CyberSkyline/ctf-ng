import {
  Card,
  Flex,
  Text,
  Separator,
} from '@radix-ui/themes';
import { map } from 'lodash';
import type { TicketMessage } from '@/types';
import { twMerge } from 'tailwind-merge';
import styles from './ticketMessagesCard.module.css';

export default function TicketMessagesCard({
  messages,
  currentUserId,
  className,
}: {
  messages: TicketMessage[],
  currentUserId: number,
  className?: string,
}) {
  return (
    <div>
      {map(messages, (message) => (
        <Card
          className={
            twMerge(
              message.author_id === currentUserId ? styles.cardSelf : styles.cardResponder,
              'mb-2',
              className,
            )
          }
          key={message.id}
        >
          <Flex justify="between">
            <Text weight="bold" size="2">{message.author_name}</Text>
            <Text weight="bold" size="2">{new Date(message.created_at).toString()}</Text>
          </Flex>
          <Separator size="4" className="mb-1" />
          <Text as="p">
            {message.text}
          </Text>
        </Card>
      ))}
    </div>
  );
}
