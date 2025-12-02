import { useFileUrl } from '@/hooks/fileuploads';
import type { Event } from '@/types';
import { AspectRatio, Skeleton } from '@radix-ui/themes';
import { twMerge } from 'tailwind-merge';
import { ErrorCallout } from './Callouts';

export default function EventGraphic({ event, className }: {event: Event, className ?: string}) {
  // aspect ratio for event card graphics
  const RATIO = 1 / 1.446015424;

  const { data : fileUrl, error : fileUrlError, isLoading } = useFileUrl('event-cards', event.image ?? undefined);

  if (!event.image) return null;

  if (fileUrlError) {
    return <ErrorCallout>Failed to load image.</ErrorCallout>;
  }

  return (
    <Skeleton loading={isLoading}>
      <div className={twMerge(className, 'overflow-clip')}>
        <AspectRatio ratio={RATIO}>
          {fileUrl?.url && (
            <img
              className="object-contain h-full w-full"
              src={fileUrl?.url}
              alt=""
            />
          )}
        </AspectRatio>
      </div>
    </Skeleton>
  );
}
