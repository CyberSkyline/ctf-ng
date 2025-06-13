import { Container } from '@radix-ui/themes';

export default function HeaderContainer({ children = undefined }: {
  children?: React.ReactNode
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
      className="bg-[var(--gray-2)] bg-radial from-[var(--gray-3)] from-[1px] to-transparent to-0% bg-size-[4px_4px] bg-repeat-space"
    >
      {children}
    </Container>
    )
  );
}
