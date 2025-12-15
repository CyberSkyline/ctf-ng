import faviconDark from '@/assets/favicons/favicon-dark.png';
import faviconLight from '@/assets/favicons/favicon-light.png';
import { useTheme } from 'next-themes';

export default function Favicon() {
  const { systemTheme } = useTheme();

  return <link rel="icon" href={systemTheme === 'dark' ? faviconDark : faviconLight} />;
}
