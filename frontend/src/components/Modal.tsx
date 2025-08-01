import { COLOR_POSITIVE, type AccentColor } from '@/constants';
import {
  Box,
  Button,
  Dialog,
  Flex,
} from '@radix-ui/themes';
import { Form } from 'radix-ui';
import { useEffect, useState, type ReactNode } from 'react';
import { TbX } from 'react-icons/tb';
import { ErrorCallout } from './Callouts';

interface ModalProps {
  title: string,
  description?: string,
  children?: ReactNode,
  trigger: ReactNode,
  onSubmit?: (formData: FormData) => Promise<unknown>,
  onOpenChange?: (open: boolean) => void,
  submitVerb?: string,
  submitColor?: AccentColor,
  submitDisabled?: boolean,
  requireTouchingForm?: boolean,
}

export default function Modal({
  title,
  description,
  children,
  trigger,
  onSubmit,
  onOpenChange,
  submitVerb = 'Submit',
  submitColor = COLOR_POSITIVE,
  submitDisabled = false,
  requireTouchingForm = false,
} : ModalProps) {
  const [ open, setOpen ] = useState<boolean>(false);
  const [ error, setError ] = useState<string | null>(null);
  const [ loading, setLoading ] = useState<boolean>(false);
  const [ formTouched, setFormTouched ] = useState<boolean>(false);

  useEffect(() => {
    if (!open) {
      // reset state when modal closes
      setFormTouched(false);
      setError(null);
    }
  }, [ open ]);

  return (
    <Dialog.Root open={open} onOpenChange={(o) => { onOpenChange?.(o); setOpen(o); }}>
      <Dialog.Trigger>
        {trigger}
      </Dialog.Trigger>

      <Dialog.Content
        className="flex flex-col gap-3"
        // aria-describedby should be set to undefined if no description is provided, otherwise it should not be set at all.
        // as far as i know, prop spreading is the only way to accomplish this.
        // eslint-disable-next-line react/jsx-props-no-spreading
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
        <Form.Root
          className="flex flex-col gap-3"
          onSubmitCapture={(e) => {
            e.preventDefault();

            if (onSubmit) {
              const formData = new FormData(e.currentTarget);
              setLoading(true);
              onSubmit(formData)
                .then(() => {
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
          }}
          onChange={() => {
            setFormTouched(true);
          }}
        >
          {children}
          <Flex direction="row-reverse" justify="start" align="center" gap="2">
            <Form.Submit asChild>
              <Button
                type="submit"
                color={onSubmit ? submitColor : 'gray'}
                variant={onSubmit ? 'solid' : 'soft'}
                loading={loading}
                disabled={loading || submitDisabled || (requireTouchingForm && !formTouched)}
              >
                {onSubmit ? submitVerb : 'Close'}
              </Button>
            </Form.Submit>
            {onSubmit && (
              <Dialog.Close>
                <Button type="button" variant="soft" color="gray">
                  Cancel
                </Button>
              </Dialog.Close>
            )}
          </Flex>
        </Form.Root>
      </Dialog.Content>
    </Dialog.Root>
  );
}
