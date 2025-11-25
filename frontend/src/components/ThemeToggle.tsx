import { useTheme } from 'next-themes';
import { NavigationMenu } from 'radix-ui';
import { TbMoon, TbSun, TbSunMoon } from 'react-icons/tb';
import { twMerge } from 'tailwind-merge';

export default function ThemeToggle({ triggerClassName, contentClassName, contentItemClassName }
  : {triggerClassName: string, contentClassName: string, contentItemClassName: string}) {
  const { theme, resolvedTheme, setTheme } = useTheme();

  const themes = {
    light : {
      name : 'Light',
      icon : TbSun,
    },
    dark : {
      name : 'Dark',
      icon : TbMoon,
    },
    system : {
      name : 'System',
      icon : TbSunMoon,
    },
  };

  // use resolvedTheme to show the actual active theme icon (in case of "system" theme)
  // sun/moon are a clearer signifier for a theme switcher than a mixed icon is
  const ActiveIcon = themes[resolvedTheme as keyof typeof themes].icon;

  return (
    <NavigationMenu.Item value="theme" className="relative">
      <NavigationMenu.Trigger
        className={twMerge(triggerClassName, 'h-full')}
        onPointerMove={(event) => event.preventDefault()}
        onPointerLeave={(event) => event.preventDefault()}
      >
        <ActiveIcon aria-label="Theme Selector" />
      </NavigationMenu.Trigger>
      <NavigationMenu.Content
        onPointerEnter={(event) => event.preventDefault()}
        onPointerLeave={(event) => event.preventDefault()}
        className={twMerge(contentClassName, 'flex flex-col gap-2')}
      >
        {Object.entries(themes).map(([ key, { name, icon : Icon } ]) => (
          <NavigationMenu.Item
            asChild
            key={key}
            onClick={() => setTheme(key)}
            className={twMerge(contentItemClassName, theme === key && '!bg-(--accent-9) !text-(--accent-contrast)')}
          >
            <button type="button">
              <Icon />
              {' '}
              {name}
            </button>
          </NavigationMenu.Item>
        ))}
      </NavigationMenu.Content>
    </NavigationMenu.Item>
  );
}
