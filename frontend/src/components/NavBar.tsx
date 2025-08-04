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

  const dropdownClass = 'flex items-center gap-2 px-2 py-1.5 rounded';

  return (
    <NavigationMenu.Root className="h-[var(--NavBarHeight)]">
      <NavigationMenu.List className="flex p-1 pr-4 dark:border-b-(--gray-a6) dark:border-b-1">
        <div className="flex">
          <NavLink to="/" className={location.pathname === '/' ? activeLinkClass : defaultLinkClass}>
            <NavigationMenu.Item>
              Dashboard
            </NavigationMenu.Item>
          </NavLink>
          <NavLink to="/events" className={location.pathname === '/events' ? activeLinkClass : defaultLinkClass}>
            <NavigationMenu.Item>
              Events
            </NavigationMenu.Item>
          </NavLink>
          <NavLink className={location.pathname === '/practice' ? activeLinkClass : defaultLinkClass}>
            <NavigationMenu.Item>
              Practice*
            </NavigationMenu.Item>
          </NavLink>
        </div>
        <div className="flex ml-auto">
          <NavLink to="/support" className={location.pathname === '/support' ? activeLinkClass : defaultLinkClass}>
            <NavigationMenu.Item>
              Support
            </NavigationMenu.Item>
          </NavLink>
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
                  className={dropdownClass}
                >
                  Profile*
                </NavLink>
              </DropdownMenu.Item>
              <DropdownMenu.Item asChild>
                <NavLink
                  to="/admin"
                  className={dropdownClass}
                >
                  Admin Portal
                </NavLink>
              </DropdownMenu.Item>
              <DropdownMenu.Separator className="h-px bg-gray-200 my-1" />
              <DropdownMenu.Item asChild>
                <button
                  type="button"
                  onClick={logout}
                  className={dropdownClass}
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
