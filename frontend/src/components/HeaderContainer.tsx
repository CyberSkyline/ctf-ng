import { Container } from '@radix-ui/themes';
import { Children, type ReactNode } from 'react';

export default function HeaderContainer({ children = undefined }: {
  children?: ReactNode
}) {
  return (
    Children.toArray(children).length > 0 && (
      <Container
        size="2"
        px="3"
        py="9"
        mx="-3"
        mt="-3"
        mb="3"
        className="bg-dots-2 shadow dark:shadow-none has-[.rt-ContainerInner:empty]:hidden"
      >
        {children}
      </Container>
    )
  );
}
