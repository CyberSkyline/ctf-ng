import { NavigationMenu } from 'radix-ui';
import { DropdownMenu } from '@radix-ui/themes';
import { NavLink, useLocation } from 'react-router';
import { TbUserCircle } from 'react-icons/tb';
import { twMerge } from 'tailwind-merge';

export default function NavBar() {
  const logout = () => {
    // perform a logout
  };

  const location = useLocation();

  const defaultLinkClass = `
    p-2
    hover:bg-(--gray-3)
    dark:hover:bg-(--gray-3)
    dark:hover:text-(--gray-12)
    text-(--gray-a11)
    dark:text-(--gray-a11)`;

  const activeLinkClass = `
    p-2
    hover:bg-(--gray-3)
    dark:hover:bg-(--gray-3)
    text-(--gray-a11)
    dark:text-(--gray-12)
    underline
    decoration-(--accent-indicator)
    underline-offset-8
    decoration-2`;

  return (
    <NavigationMenu.Root className="h-[var(--NavBarHeight)]">
      <NavigationMenu.List className="flex p-1 pr-4 dark:border-b-(--gray-a6) dark:border-b-1">
        <div className="flex">
          <NavigationMenu.Item className={location.pathname === '/' ? activeLinkClass : defaultLinkClass}>
            <NavLink to="/">
              Dashboard
            </NavLink>
          </NavigationMenu.Item>
          <NavigationMenu.Item className={location.pathname === '/events' ? activeLinkClass : defaultLinkClass}>
            <NavLink to="/events">
              Events
            </NavLink>
          </NavigationMenu.Item>
          <NavigationMenu.Item className={location.pathname === '/practice' ? activeLinkClass : defaultLinkClass}>
            Practice*
          </NavigationMenu.Item>
        </div>
        <div className="flex ml-auto">
          <NavigationMenu.Item className={location.pathname === '/support' ? activeLinkClass : defaultLinkClass}>
            <NavLink to="/support">
              Support
            </NavLink>
          </NavigationMenu.Item>
          <NavigationMenu.Item className={location.pathname === '/notifications' ? activeLinkClass : defaultLinkClass}>
            Notifications*
          </NavigationMenu.Item>

          <DropdownMenu.Root>
            <DropdownMenu.Trigger>
              <NavigationMenu.Item className={twMerge(defaultLinkClass, 'pt-3')}>
                <TbUserCircle />
              </NavigationMenu.Item>
            </DropdownMenu.Trigger>
            <DropdownMenu.Content
              className="mt-2 rounded-md shadow-lg p-2 border"
            >
              <DropdownMenu.Item asChild>
                <NavLink
                  // to="/profile"
                  className="flex items-center gap-2 px-2 py-1.5 rounded"
                >
                  Profile*
                </NavLink>
              </DropdownMenu.Item>

              <DropdownMenu.Item asChild>
                <NavLink
                  to="/admin"
                  className="flex items-center gap-2 px-2 py-1.5 rounded"
                >
                  Admin Portal
                </NavLink>
              </DropdownMenu.Item>
              <DropdownMenu.Separator className="h-px bg-gray-200 my-1" />
              <DropdownMenu.Item asChild>
                <button
                  type="button"
                  onClick={logout}
                  className="w-full flex items-center gap-2 px-2 py-1.5 rounded"
                >
                  Log Out*
                </button>
              </DropdownMenu.Item>
            </DropdownMenu.Content>
          </DropdownMenu.Root>
        </div>
        <NavigationMenu.Indicator className="NavigationMenuIndicator" />
      </NavigationMenu.List>
    </NavigationMenu.Root>
  );
}
