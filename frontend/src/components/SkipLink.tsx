import type { MouseEvent } from 'react';
import { twMerge } from 'tailwind-merge';

/**
 * First focusable element on every page: lets keyboard users jump past the
 * navigation bar to the main landmark (WCAG 2.4.1). Visible only while focused.
 * Focus is moved in a handler instead of following "#main", so the URL hash
 * stays untouched.
 */
export default function SkipLink() {
  const skip = (event: MouseEvent<HTMLAnchorElement>) => {
    event.preventDefault();
    document.getElementById('main')?.focus();
  };

  return (
    <a
      href="#main"
      onClick={skip}
      className={twMerge(
        'sr-only focus:not-sr-only focus:fixed focus:left-2 focus:top-1.5 focus:z-50',
        'focus:rounded-md focus:px-3.5 focus:py-2 focus:font-medium focus:shadow-lg',
        'focus:bg-(--color-panel-solid) focus:text-(--gray-12) focus:outline-2 focus:outline-(--accent-9)',
      )}
    >
      Skip to content
    </a>
  );
}
