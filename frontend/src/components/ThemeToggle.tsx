import { useTheme } from 'next-themes';
import { NavigationMenu } from 'radix-ui';
import {
  TbCheck,
  TbMoon,
  TbSun,
  TbSunMoon,
} from 'react-icons/tb';
import { twMerge } from 'tailwind-merge';

export default function ThemeToggle({
  itemClassName, triggerClassName, contentClassName, contentItemClassName,
}: {
  itemClassName?: string,
  triggerClassName: string,
  contentClassName: string,
  contentItemClassName: string,
}) {
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
    <NavigationMenu.Item value="theme" className={twMerge('relative', itemClassName)}>
      <NavigationMenu.Trigger
        className={twMerge(triggerClassName, 'h-full')}
        onPointerMove={(event) => event.preventDefault()}
        onPointerLeave={(event) => event.preventDefault()}
        aria-label="Theme Selector"
      >
        <ActiveIcon aria-hidden="true" />
      </NavigationMenu.Trigger>
      <NavigationMenu.Content
        onPointerEnter={(event) => event.preventDefault()}
        onPointerLeave={(event) => event.preventDefault()}
        className={twMerge(contentClassName, 'flex flex-col gap-2')}
      >
        {/* The selection is conveyed by aria-pressed, a check and weight, not by color alone (WCAG 1.4.1). */}
        {Object.entries(themes).map(([ key, { name, icon : Icon } ]) => {
          const selected = theme === key;

          return (
            <NavigationMenu.Item
              asChild
              key={key}
              onClick={() => setTheme(key)}
              className={twMerge(contentItemClassName, selected && 'font-semibold !text-(--gray-12)')}
            >
              <button type="button" aria-pressed={selected}>
                <Icon aria-hidden="true" />
                {name}
                <TbCheck aria-hidden="true" className={twMerge('ml-auto pl-2 box-content text-(--accent-11)', !selected && 'invisible')} />
              </button>
            </NavigationMenu.Item>
          );
        })}
      </NavigationMenu.Content>
    </NavigationMenu.Item>
  );
}
