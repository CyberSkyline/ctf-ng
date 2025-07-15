import { Flex, Heading } from '@radix-ui/themes';
import { useEffect, useRef, type ReactNode } from 'react';

export default function AdminSidebar({ children, title }: {children: ReactNode, title: string}) {
  const headerRef = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    // Steal focus when the sidebar is mounted
    // Allows keyboard navigation without having to tab through the entire table
    headerRef.current?.focus();
  }, []);

  return (
    <Flex direction="column" gap="4" className="basis-1/2 min-w-128 grow-0 shrink-0 overflow-y-auto">
      <Heading ref={headerRef} tabIndex={-1}>{title}</Heading>
      {children}
    </Flex>
  );
}
