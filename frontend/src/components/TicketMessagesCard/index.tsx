import type { TicketMessage } from '@/types';
import {
  Card,
  Flex,
  Separator,
  Text,
} from '@radix-ui/themes';
import RadixMarkdown from 'components/RadixMarkdown';
import { map } from 'lodash';
import { twMerge } from 'tailwind-merge';

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
              message.author_id === currentUserId ? '' : 'outline outline-(--accent-8)',
              'mb-2',
              className,
            )
          }
          key={message.id}
        >
          <Flex justify="between">
            <Text weight="bold" size="2">{message.author_name}</Text>
            <Text weight="bold" size="2">{message.created_at.toLocaleString()}</Text>
          </Flex>
          <Separator size="4" className="mb-1" />
          <RadixMarkdown>
            {message.text}
          </RadixMarkdown>
        </Card>
      ))}
    </div>
  );
}
