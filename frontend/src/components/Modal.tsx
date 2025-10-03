import { COLOR_POSITIVE, type AccentColor } from '@/constants';
import {
  Box,
  Button,
  Dialog,
  Flex,
} from '@radix-ui/themes';
import { useEffect, useState, type ReactNode } from 'react';
import {
  useForm,
  type DefaultValues,
  type FieldValues,
  type UseFormReturn,
} from 'react-hook-form';
import { TbX } from 'react-icons/tb';
import { twMerge } from 'tailwind-merge';
import { ErrorCallout } from './Callouts';

interface ModalProps<T extends FieldValues> {
  title: string,
  description?: string,
  children?: ReactNode | ((rhf: UseFormReturn<T>) => ReactNode),
  trigger: ReactNode,
  className?: string,
  defaultValues?: DefaultValues<T>,
  onSubmit?: (data: T) => Promise<unknown>,
  onOpenChange?: (open: boolean) => void,
  defaultOpen?: boolean,
  submitVerb?: string,
  submitColor?: AccentColor,
  submitDisabled?: boolean,
}

export default function Modal<T extends FieldValues>({
  title,
  description,
  children,
  trigger,
  className,
  defaultValues,
  onSubmit,
  onOpenChange,
  defaultOpen = false,
  submitVerb = 'Submit',
  submitColor = COLOR_POSITIVE,
  submitDisabled = false,
} : ModalProps<T>) {
  const [ open, setOpen ] = useState<boolean>(defaultOpen);
  const [ error, setError ] = useState<string | null>(null);
  const [ loading, setLoading ] = useState<boolean>(false);

  const rhf = useForm<T>({
    mode : 'onBlur',
    defaultValues,
  });

  useEffect(() => {
    if (open) {
      // reset state when modal opens
      setError(null);
      setLoading(false);
      rhf.reset(defaultValues);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ open ]);

  return (
    <Dialog.Root open={open} onOpenChange={(o) => { onOpenChange?.(o); setOpen(o); }}>
      <Dialog.Trigger>
        {trigger}
      </Dialog.Trigger>

      <Dialog.Content
        className={twMerge('flex flex-col gap-3', className)}
        // aria-describedby should be set to undefined if no description is provided, otherwise it should not be set at all.
        // as far as i know, prop spreading is the only way to accomplish this.
        {
          ...(!description ? { 'aria-describedby' : undefined } : {})
        }
      >
        <Box>
          <Flex direction="row" justify="between" align="center">
            <Dialog.Title mb="0">{title}</Dialog.Title>
            <Dialog.Close>
              <Button
                type="button"
                aria-label="Close"
                variant="ghost"
                color="gray"
                className="!m-0 !p-1"
              >
                <TbX className="text-xl" />
              </Button>
            </Dialog.Close>
          </Flex>
          {description && (
          <Dialog.Description color="gray">
            {description}
          </Dialog.Description>
          )}
        </Box>
        {error && (
          <ErrorCallout>
            {error}
          </ErrorCallout>
        )}

        <form
          className="flex flex-col gap-3"
          onSubmit={rhf.handleSubmit((data) => {
            if (onSubmit) {
              setLoading(true);
              onSubmit(data).then(() => {
                // if promise resolves, close the modal
                setOpen(false);
              })
                .catch((err) => {
                  // if promise rejects, set the error message
                  setError(err.message);
                }).finally(() => {
                  setLoading(false);
                });
            } else {
              // if no submit handler is defined, just close the modal
              setOpen(false);
            }
          })}
        >
          {typeof children === 'function' ? children(rhf) : children}
          <Flex direction="row-reverse" justify="start" align="center" gap="2">
            <Button
              type="submit"
              color={onSubmit ? submitColor : 'gray'}
              variant={onSubmit ? 'solid' : 'soft'}
              loading={loading}
              disabled={
                loading || submitDisabled
              }
            >
              {onSubmit ? submitVerb : 'Close'}
            </Button>
            {onSubmit && (
              <Dialog.Close>
                <Button type="button" variant="soft" color="gray">
                  Cancel
                </Button>
              </Dialog.Close>
            )}
          </Flex>
        </form>
      </Dialog.Content>
    </Dialog.Root>
  );
}
