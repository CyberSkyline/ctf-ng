import {
  Button, Dialog, Flex,
} from '@radix-ui/themes';
import { useState, type ReactNode } from 'react';
import { FaXmark } from 'react-icons/fa6';

interface ModalProps {
  title: string,
  buttonText: string,
  children: ReactNode,
  onSubmit: () => void,
  onSubmitText: string,
  onSubmitColor?: 'lime' | 'red'
}

export default function Modal({
  title, buttonText, children, onSubmit, onSubmitText, onSubmitColor = 'lime',
}:ModalProps) {
  const [open, setOpen] = useState<boolean>(false);

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Trigger>
        <Button>{buttonText}</Button>
      </Dialog.Trigger>

      <Dialog.Content aria-describedby={undefined}>
        <Flex direction="row">
          <Dialog.Title
            className="pb-2"
          >
            {title}
          </Dialog.Title>
          <Dialog.Close>
            <button type="button" aria-label="Close" className="absolute left-auto right-4 top-4">
              <FaXmark />
            </button>
          </Dialog.Close>
        </Flex>
        {children}
        <Flex gap="3" mt="3" justify="end">
          <Dialog.Close>
            <Button variant="solid" color="gray">
              Cancel
            </Button>
          </Dialog.Close>
          <Button
            color={onSubmitColor}
            onClick={() => {
              onSubmit();
              setOpen(false);
            }}
          >
            {onSubmitText}
          </Button>
        </Flex>
      </Dialog.Content>
    </Dialog.Root>
  );
}
