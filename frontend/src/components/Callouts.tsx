import { Callout } from '@radix-ui/themes';
import type { ReactNode } from 'react';
import { TbAlertTriangle, TbCancel, TbInfoCircle } from 'react-icons/tb';

export function ErrorCallout({ children }: {children: ReactNode}) {
  return (
    <Callout.Root variant="surface" color="red">
      <Callout.Icon>
        <TbCancel aria-label="Error" />
      </Callout.Icon>
      <Callout.Text className="whitespace-pre-wrap">
        {children}
      </Callout.Text>
    </Callout.Root>
  );
}

export function WarningCallout({ children }: {children: ReactNode}) {
  return (
    <Callout.Root variant="surface" color="amber">
      <Callout.Icon>
        <TbAlertTriangle aria-label="Warning" />
      </Callout.Icon>
      <Callout.Text className="whitespace-pre-wrap">
        {children}
      </Callout.Text>
    </Callout.Root>
  );
}
export function InfoCallout({ children }: {children: ReactNode}) {
  return (
    <Callout.Root variant="surface" color="jade">
      <Callout.Icon>
        <TbInfoCircle aria-label="Info" />
      </Callout.Icon>
      <Callout.Text className="whitespace-pre-wrap">
        {children}
      </Callout.Text>
    </Callout.Root>
  );
}
