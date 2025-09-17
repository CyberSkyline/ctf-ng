import { Flex } from '@radix-ui/themes';
import { useEffect, useRef, type ReactNode } from 'react';

export default function AdminSidebar({ basis, children }: {basis?: string, children: ReactNode}) {
  const headerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Steal focus when the sidebar is mounted
    // Allows keyboard navigation without having to tab through the entire table
    headerRef.current?.focus();
  }, []);

  return (
    <Flex
      direction="column"
      gap="3"
      className="min-w-128 overflow-y-auto outline-0 -m-3 p-3"
      ref={headerRef}
      tabIndex={-1}
      flexBasis={basis || '50%'}
    >
      {children}
    </Flex>
  );
}
