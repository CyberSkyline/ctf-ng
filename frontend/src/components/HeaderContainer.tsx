import { Container } from '@radix-ui/themes';
import type { ReactNode } from 'react';

export default function HeaderContainer({ children = undefined }: {
  children?: ReactNode
}) {
  return (
    children && (
      <Container
        size="2"
        px="4"
        py="9"
        mx="-4"
        mt="-4"
        mb="4"
        className="bg-dots-2"
      >
        {children}
      </Container>
    )
  );
}
