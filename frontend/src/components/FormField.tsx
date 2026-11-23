import { COLOR_NEGATIVE } from '@/constants';
import { Flex, Text } from '@radix-ui/themes';
import { useId, type ReactNode } from 'react';
import type { FieldError } from 'react-hook-form';

export default function FormField({
  children,
  label,
  rightComponent,
  error,
}: {
  /**
   * Renders the control. `injected` is spread onto native-style controls. `labelId` is for controls a
   * <label for> can't name (radio groups, segmented controls, contenteditable editors): pass it as aria-labelledby.
   */
  children: (injected: {
    id: string;
    'aria-describedby'?: string;
    'aria-errormessage'?: string;
    'aria-invalid': 'true' | 'false';
  }, extras: { labelId: string | undefined }) => React.ReactNode,
  label: string | null,
  rightComponent?: ReactNode,
  error?: FieldError,
}) {
  const id = useId(); // Unique ID for accessibility linking
  const errorId = `${id}-error`;
  const labelId = label ? `${id}-label` : undefined;

  const injected = {
    id,
    'aria-describedby' : error ? errorId : undefined,
    'aria-errormessage' : error ? errorId : undefined,
    'aria-invalid' : (error ? 'true' : 'false') as 'true' | 'false',
  };

  return (
    <Flex direction="column" gap="1">
      <Flex direction="row" justify="between" align="end" className="empty:hidden">
        {label && <label htmlFor={id} id={labelId} data-invalid={error ? 'true' : 'false'}>{label}</label>}
        {rightComponent}
      </Flex>
      {children(injected, { labelId })}
      {/*
        Always mounted and never display:none, so it stays in the accessibility tree and the live region exists
        before the error text arrives (WCAG 3.3.1). While empty it is sr-only, which takes it out of the flex
        flow so it adds no gap.
      */}
      <Text as="span" color={COLOR_NEGATIVE} id={errorId} aria-live="polite" aria-atomic className="empty:sr-only">
        {error ? (error.message || 'Invalid input') : null}
      </Text>
    </Flex>
  );
}
