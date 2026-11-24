import { useEffect, useState } from 'react';

/**
 * App-wide polite announcements for screen readers (WCAG 4.1.3).
 *
 * A live region only reliably announces text that changes inside an element that already exists, so a single
 * region is mounted once (in main.tsx) and messages are written into it. Use this for status messages that have
 * no persistent place on the page: socket pushes, save confirmations, connection status.
 *
 * Errors that interrupt (role="alert") don't need this: alerts are announced when inserted.
 */

const ANNOUNCE_DELAY_MS = 100;
const CLEAR_AFTER_MS = 7000;

let write: ((message: string) => void) | null = null;

/** Announce a message politely. Safe to call from outside React (e.g. socket handlers). */
export function announce(message: string) {
  write?.(message);
}

/** Hook form of {@link announce}, for components. */
export function useAnnounce() {
  return announce;
}

export default function LiveAnnouncer() {
  const [ text, setText ] = useState('');

  useEffect(() => {
    let showTimer: ReturnType<typeof setTimeout> | undefined;
    let clearTimer: ReturnType<typeof setTimeout> | undefined;

    write = (message: string) => {
      clearTimeout(showTimer);
      clearTimeout(clearTimer);
      // Empty the region first so an identical message is announced again.
      setText('');
      showTimer = setTimeout(() => {
        setText(message);
        // Clear stale text so users browsing into the region later don't read old messages.
        clearTimer = setTimeout(() => setText(''), CLEAR_AFTER_MS);
      }, ANNOUNCE_DELAY_MS);
    };

    return () => {
      write = null;
      clearTimeout(showTimer);
      clearTimeout(clearTimer);
    };
  }, []);

  return (
    <div role="status" aria-live="polite" aria-atomic="true" className="sr-only">
      {text}
    </div>
  );
}
