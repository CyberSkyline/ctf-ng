import { COLOR_NEGATIVE } from '@/constants';
import { Flex, Text } from '@radix-ui/themes';
import { useId } from 'react';
import type { FieldError } from 'react-hook-form';

export default function FormField({
  children,
  label,
  rightLabel,
  error,
}: {
  children: (injected: { id: string; 'aria-describedby'?: string; 'aria-invalid': 'true' | 'false' }) => React.ReactNode,
  label: string | null,
  rightLabel?: string,
  error?: FieldError,
}) {
  const id = useId(); // Unique ID for accessibility linking

  const injected = {
    id,
    'aria-errormessage' : error ? `${id}-error` : undefined,
    'aria-invalid' : (error ? 'true' : 'false') as 'true' | 'false',
  };

  return (
    <Flex direction="column" gap="1">
      <Flex direction="row" justify="between" align="end" className="empty:hidden">
        {label && <label htmlFor={id} data-invalid={error ? 'true' : 'false'}>{label}</label>}
        {rightLabel && <Text size="2" color={rightLabel.startsWith('-') ? 'red' : 'gray'}>{rightLabel}</Text>}
      </Flex>
      {children(injected)}
      {error && <Text as="span" color={COLOR_NEGATIVE} id={`${id}-error`} aria-live="polite" aria-atomic>{error.message || 'Invalid input'}</Text>}
    </Flex>
  );
}
