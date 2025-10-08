import { apiMutation } from '@/fetchers';
import { useAuth } from '@/hooks/users';
import ThemeToggle from 'components/ThemeToggle';
import { useTheme } from 'next-themes';
import { NavigationMenu } from 'radix-ui';
import { TbUserCircle } from 'react-icons/tb';
import { NavLink, useLocation } from 'react-router';
import { twMerge } from 'tailwind-merge';

export default function NavBar() {
  const logout = () => {
    apiMutation('/users/logout', {}, { method : 'POST' }).then(() => {
      // do a full reload to make sure window.init is updated
      window.location.href = '/';
    });
  };

  const { isAuthenticated, isUnauthenticated, user } = useAuth();

  const location = useLocation();
  const { theme } = useTheme(); // Drop Content wouldn't obey otherwise

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

  const contentBase = `
    absolute 
    top-full 
    mt-1
    z-50 
    max-w-[90vw] 
    right-4 
    rounded-md 
    shadow-lg
    border-(--gray-a6)
    border-1
  `;

  const contentLight = `
    bg-white
    text-(--gray-a11)
  `;

  const contentDark = `
    dark:bg-black
    dark:text-(--gray-12)
  `;

  const contentItem = `
    w-full
    flex
    items-center
    gap-2
    px-2
    py-1.5
    rounded
    hover:bg-(--gray-3)
    dark:hover:bg-(--gray-3)
    dark:hover:text-(--gray-12)
    text-(--gray-a11)
    dark:text-(--gray-a11)
  `;

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
          {/* <NavLink className={location.pathname === '/practice' ? activeLinkClass : defaultLinkClass}>
            <NavigationMenu.Item>
              Practice*
            </NavigationMenu.Item>
          </NavLink> */}
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

          <NavigationMenu.Item>
            <NavigationMenu.Trigger className={defaultLinkClass}>
              <TbUserCircle className="inline" />
              {user && ` ${user.name}`}
            </NavigationMenu.Trigger>
            <NavigationMenu.Content className={twMerge(contentBase, theme === 'dark' ? contentDark : contentLight)}>
              <ul className="grid gap-2 p-3">
                <li>
                  <NavLink
                    to="/profile"
                    className={contentItem}
                  >
                    Profile*
                  </NavLink>
                </li>
                <li>
                  <NavLink
                    to="/admin"
                    className={contentItem}
                  >
                    Admin Portal
                  </NavLink>
                </li>
                <li>
                  <ThemeToggle className="ml-3 py-2" />
                </li>

                {isAuthenticated && (
                  <li>
                    <button
                      type="button"
                      onClick={logout}
                      className={contentItem}
                    >
                      Log Out
                    </button>
                  </li>
                )}
                {isUnauthenticated && (
                  <li>
                    <NavLink
                      to="/login"
                      className={contentItem}
                    >
                      Log In
                    </NavLink>
                  </li>
                )}
              </ul>
            </NavigationMenu.Content>
          </NavigationMenu.Item>
        </div>
        <NavigationMenu.Indicator />
      </NavigationMenu.List>
    </NavigationMenu.Root>
  );
}
