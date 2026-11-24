import {
  Box,
  Flex,
  Heading,
  Text,
} from '@radix-ui/themes';
import { useEffect, useId, useState } from 'react';
import { twMerge } from 'tailwind-merge';

export default function Timer(
  {
    target,
    size = '6',
    onEnd,
  } : {
    target: Date | null,
    size?: React.ComponentProps<typeof Heading>['size'],
    onEnd?: () => void
  },
) {
  const [ timerString, setTimerString ] = useState('');
  const [ hidden, setHidden ] = useState(false);
  const descriptionId = useId();

  useEffect(() => {
    let interval: number | undefined;

    const updateTimer = () => {
      if (!target) {
        setTimerString('0:00:00');
        return;
      }

      const now = new Date();
      const diff = target.getTime() - now.getTime();

      if (diff <= 0) {
        setTimerString('0:00:00');
        clearInterval(interval);
        if (onEnd) onEnd();
        return;
      }

      const hours = String(Math.floor(diff / (1000 * 60 * 60))).padStart(1, '0');
      const minutes = String(Math.floor((diff / (1000 * 60)) % 60)).padStart(2, '0');
      const seconds = String(Math.floor((diff / 1000) % 60)).padStart(2, '0');

      setTimerString(`${hours}:${minutes}:${seconds}`);
    };

    updateTimer();

    // if there's no target date, do not set interval
    if (!target) return () => {};

    // if hidden, do not set interval
    if (hidden) return () => {};

    // set interval to update periodically
    // we update more than once a second for better accuracy and to avoid skipped seconds
    interval = setInterval(updateTimer, 250);
    return () => clearInterval(interval);
  }, [ target, hidden, onEnd ]);

  // The visible digits are one box per character, which screen readers would spell out, so the button gets a
  // stable name and pressed state, and the current time is its description (WCAG 1.3.1, 4.1.2). The description
  // isn't a live region, so the per-second updates stay silent until the user focuses the button. (A role on the
  // span would be ignored anyway: a button's children are presentational.)
  return (
    <button
      type="button"
      onClick={() => setHidden(!hidden)}
      aria-label="Hide time remaining"
      aria-pressed={hidden}
      aria-describedby={descriptionId}
      className="block group"
    >
      <span id={descriptionId} className="sr-only">
        {hidden ? 'Time remaining is hidden' : timerString}
      </span>
      <Flex direction="row" gap="1" align="center" aria-hidden="true">
        { timerString.split('').map((part, index) => (
          <Box
            // eslint-disable-next-line react/no-array-index-key
            key={index}
            className={
              twMerge(
                part !== ':' && 'bg-(--gray-a3) group-hover:bg-(--gray-a5) px-1.5 font-bold',
                'py-0.5 rounded select-none',
              )
            }
          >
            <Text size={size} className="tabular-nums">
              {hidden && part !== ':' ? '-' : part}
            </Text>
          </Box>
        ))}
      </Flex>
    </button>
  );
}
