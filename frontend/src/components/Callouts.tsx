import { Callout } from '@radix-ui/themes';
import type { ReactNode } from 'react';
import { TbAlertTriangle, TbCancel, TbInfoCircle } from 'react-icons/tb';
import { COLOR_INFO, COLOR_NEGATIVE, COLOR_WARNING } from '@/constants';

export function ErrorCallout({ children, className }: {children: ReactNode, className?: string}) {
  return (
    <Callout.Root variant="surface" color={COLOR_NEGATIVE} className={className}>
      <Callout.Icon>
        <TbCancel aria-label="Error" />
      </Callout.Icon>
      <Callout.Text className="whitespace-pre-wrap">
        {children}
      </Callout.Text>
    </Callout.Root>
  );
}

export function WarningCallout({ children, className }: {children: ReactNode, className?: string}) {
  return (
    <Callout.Root variant="surface" color={COLOR_WARNING} className={className}>
      <Callout.Icon>
        <TbAlertTriangle aria-label="Warning" />
      </Callout.Icon>
      <Callout.Text className="whitespace-pre-wrap">
        {children}
      </Callout.Text>
    </Callout.Root>
  );
}
export function InfoCallout({ children, className }: {children: ReactNode, className?: string}) {
  return (
    <Callout.Root variant="surface" color={COLOR_INFO} className={className}>
      <Callout.Icon>
        <TbInfoCircle aria-label="Info" />
      </Callout.Icon>
      <Callout.Text className="whitespace-pre-wrap">
        {children}
      </Callout.Text>
    </Callout.Root>
  );
}
