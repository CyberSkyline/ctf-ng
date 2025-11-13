import { COLOR_NEGATIVE } from '@/constants';
import { Flex, Text } from '@radix-ui/themes';
import { useId } from 'react';
import type { FieldError } from 'react-hook-form';

export default function FormField({
  children,
  label,
  error,
}: {
  children: (injected: { id: string; 'aria-describedby'?: string; 'aria-invalid': 'true' | 'false' }) => React.ReactNode,
  label: string | null,
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
      {label && <label htmlFor={id} data-invalid={error ? 'true' : 'false'}>{label}</label>}
      {children(injected)}
      {error && <Text as="span" color={COLOR_NEGATIVE} id={`${id}-error`} aria-live="polite" aria-atomic>{error.message || 'Invalid input'}</Text>}
    </Flex>
  );
}
