import { Button, IconButton, Tooltip } from '@radix-ui/themes';
import type { ComponentProps } from 'react';
import { useEffect, useRef, useState } from 'react';
import { TbCheck, TbCopy } from 'react-icons/tb';

/** How long the button stays in its "Copied" state after a successful copy. */
const COPIED_DURATION = 1500;

interface CopyButtonProps extends Pick<ComponentProps<typeof Button>, 'size' | 'variant' | 'color'> {
  /** Text placed on the clipboard. */
  value: string;
  /** Button text. Omit for an icon-only button, which gets a tooltip instead. */
  label?: string;
  /** Describes what is copied, e.g. `Copy invite link`. Defaults to the value itself. */
  'aria-label'?: string;
}

/**
 * Copies `value` to the clipboard and confirms it by swapping to a check for a moment.
 *
 * The clipboard is only available in a secure context, so a failed copy is left
 * silent - every caller renders the value where it can still be selected by hand.
 */
export default function CopyButton({
  value,
  label,
  size = '1',
  variant,
  color,
  'aria-label' : ariaLabel,
}: CopyButtonProps) {
  const [ copied, setCopied ] = useState(false);
  const timeout = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  useEffect(() => () => clearTimeout(timeout.current), []);

  const copy = () => {
    navigator.clipboard.writeText(value).then(() => {
      setCopied(true);
      clearTimeout(timeout.current);
      timeout.current = setTimeout(() => setCopied(false), COPIED_DURATION);
    }, () => { /* clipboard unavailable - the value is selectable either way */ });
  };

  const icon = copied ? <TbCheck aria-hidden /> : <TbCopy aria-hidden />;

  if (label) {
    return (
      <Button size={size} variant={variant} color={color} aria-label={ariaLabel} onClick={copy}>
        {icon}
        {copied ? 'Copied' : label}
      </Button>
    );
  }

  return (
    <Tooltip content={copied ? 'Copied' : 'Copy'}>
      <IconButton
        size={size}
        variant={variant}
        color={color}
        aria-label={ariaLabel ?? `Copy ${value}`}
        onClick={copy}
      >
        {icon}
      </IconButton>
    </Tooltip>
  );
}
