import {
  COLOR_INFO,
  COLOR_NEGATIVE,
  COLOR_POSITIVE,
  COLOR_WARNING,
  type AccentColor,
} from '@/constants';
import { Callout } from '@radix-ui/themes';
import { announce as announceMessage } from 'components/LiveAnnouncer';
import { useEffect, useRef, type ReactNode } from 'react';
import type { IconType } from 'react-icons';
import {
  TbAlertTriangle,
  TbCancel,
  TbCheck,
  TbInfoCircle,
} from 'react-icons/tb';

type CalloutProps = {
  children: ReactNode;
  className?: string;
  /**
   * Set when the callout reports the result of something the user just did (a failed submit, a saved form,
   * a search with no results), so screen readers announce it as it appears (WCAG 4.1.3).
   * Leave unset when the callout is page content, such as a load error or a standing notice: announcing those
   * on every page load is noise.
   */
  announce?: boolean;
};

function BaseCallout({
  children,
  className,
  announce,
  color,
  icon : Icon,
  iconLabel,
  liveRole,
}: CalloutProps & { color: AccentColor, icon: IconType, iconLabel: string, liveRole: 'alert' | 'status' }) {
  // role="alert" is announced reliably when the callout is inserted, so errors carry it directly.
  // role="status" is not (the region is created together with its text), so polite callouts write their text
  // into the app-wide LiveAnnouncer instead, on mount and whenever the text changes.
  const politeAnnounce = announce && liveRole === 'status';
  const textRef = useRef<HTMLParagraphElement>(null);
  const lastAnnounced = useRef<string | null>(null);

  useEffect(() => {
    if (!politeAnnounce) return;

    const text = textRef.current?.textContent?.trim();
    if (text && text !== lastAnnounced.current) {
      announceMessage(`${iconLabel}: ${text}`);
      lastAnnounced.current = text;
    }
  });

  return (
    <Callout.Root variant="surface" color={color} className={className} role={announce && liveRole === 'alert' ? 'alert' : undefined}>
      <Callout.Icon>
        <Icon aria-label={iconLabel} />
      </Callout.Icon>
      <Callout.Text className="whitespace-pre-wrap" ref={textRef}>
        {children}
      </Callout.Text>
    </Callout.Root>
  );
}

export function ErrorCallout(props: CalloutProps) {
  return <BaseCallout {...props} color={COLOR_NEGATIVE} icon={TbCancel} iconLabel="Error" liveRole="alert" />;
}

export function WarningCallout(props: CalloutProps) {
  return <BaseCallout {...props} color={COLOR_WARNING} icon={TbAlertTriangle} iconLabel="Warning" liveRole="status" />;
}

export function InfoCallout(props: CalloutProps) {
  return <BaseCallout {...props} color={COLOR_INFO} icon={TbInfoCircle} iconLabel="Info" liveRole="status" />;
}

export function SuccessCallout(props: CalloutProps) {
  return <BaseCallout {...props} color={COLOR_POSITIVE} icon={TbCheck} iconLabel="Success" liveRole="status" />;
}
