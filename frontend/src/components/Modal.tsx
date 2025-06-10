import {
  Button, Dialog, Flex,
} from '@radix-ui/themes';
import { useState, type ReactNode } from 'react';
import { RxCross2 } from "react-icons/rx";

interface ModalProps {
  title: string,
  buttonText: string,
  children: ReactNode,
  onSubmit: () => void,
  onSubmitText: string,
  onSubmitColor?: 'green' | 'red'
}

export default function Modal({
  title, buttonText, children, onSubmit, onSubmitText, onSubmitColor = 'green',
}:ModalProps) {
  const [open, setOpen] = useState<boolean>(false);

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Trigger>
        <Button>{buttonText}</Button>
      </Dialog.Trigger>

      <Dialog.Content aria-describedby={undefined}>
        <Flex direction="row">
          <Dialog.Title>{title}</Dialog.Title>
          <Dialog.Close>
            <button type="button" aria-label="Close" className="absolute left-auto right-4 top-4">
              <RxCross2 />
            </button>
          </Dialog.Close>
        </Flex>
        {children}
        <Flex gap="3" mt="3" justify="end">
          <Dialog.Close>
            <Button variant="soft" color="gray">
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
