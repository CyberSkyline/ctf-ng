import { Flex, Switch, Text } from '@radix-ui/themes';
import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';

export default function ThemeToggle({ className }: {className : string}) {
  const { theme, setTheme } = useTheme();
  const [ mounted, setMounted ] = useState(false);

  // Prevent hydration mismatch
  useEffect(() => setMounted(true), []);
  if (!mounted) return null;

  return (
    <Flex gap="2" align="center" className={className}>
      <Switch
        checked={theme === 'dark'}
        onCheckedChange={(checked) => setTheme(checked ? 'dark' : 'light')}
        aria-label="Dark Theme"
      />
      <Text
        className="dark:text-(--gray-a11)"
        size="3"
      >
        {theme.charAt(0).toUpperCase() + theme.slice(1)}
      </Text>
    </Flex>
  );
}
