import { apiMutation } from '@/fetchers';
import { useAuth } from '@/hooks/users';
import { Flex } from '@radix-ui/themes';
import NotificationsPopover from 'components/NotificationsPopover';
import ThemeToggle from 'components/ThemeToggle';
import { NavigationMenu } from 'radix-ui';
import { TbUserCircle } from 'react-icons/tb';
import { NavLink, useLocation } from 'react-router';

export default function NavBar() {
  const logout = () => {
    apiMutation('/users/logout', {}, { method : 'POST' }).then(() => {
      // do a full reload to make sure window.init is updated
      window.location.href = '/';
    });
  };

  const { isAuthenticated, isUnauthenticated, user } = useAuth();

  const location = useLocation();

  const defaultLinkClass = `
    h-full
    p-2
    hover:bg-(--gray-3)
    dark:hover:bg-(--gray-3)
    dark:hover:text-(--gray-12)
    text-(--gray-a11)
    dark:text-(--gray-a11)`;

  const activeLinkClass = `
    h-full
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
    bg-white
    text-(--gray-a11)
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

          {isAuthenticated && (
            <NotificationsPopover
              triggerClassName={defaultLinkClass}
              contentClassName={contentBase}
            />
          )}

          <NavigationMenu.Item>
            <NavigationMenu.Trigger
              className={defaultLinkClass}
              onPointerMove={(event) => event.preventDefault()}
              onPointerLeave={(event) => event.preventDefault()}
            >
              <Flex direction="row" align="center" gap="1">
                <TbUserCircle className="inline" />
                {user ? ` ${user.name}` : ' Log In'}
              </Flex>
            </NavigationMenu.Trigger>
            <NavigationMenu.Content
              className={contentBase}
              onPointerEnter={(event) => event.preventDefault()}
              onPointerLeave={(event) => event.preventDefault()}
            >
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
