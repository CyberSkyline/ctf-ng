import { useFileUrl } from '@/hooks/fileuploads';
import type { Event } from '@/types';
import { Skeleton } from '@radix-ui/themes';

export default function EventGraphic({ event, className }: {event: Event, className ?: string}) {
  const { data : fileUrl, error : fileUrlError, isLoading } = useFileUrl('event-cards', event.image ?? undefined);

  if (!event.image) return null;

  return (
    <Skeleton loading={isLoading}>
      {fileUrl?.url
        && (
          <img
            className={className}
            src={fileUrl?.url}
            alt={`Card graphic for ${event.name}`}
          />
        )}
    </Skeleton>
  );
}
