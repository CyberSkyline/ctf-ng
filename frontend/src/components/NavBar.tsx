import { COLOR_HINT, ImpersonateIcon } from '@/constants';
import { apiMutation } from '@/fetchers';
import { useGlobalPermission } from '@/hooks/permissions';
import { stopImpersonation, useAuth } from '@/hooks/users';
import { Flex, Skeleton, Text } from '@radix-ui/themes';
import NotificationsPopover from 'components/NotificationsPopover';
import { NavigationMenu } from 'radix-ui';
import { TbUserCircle } from 'react-icons/tb';
import { NavLink, useLocation } from 'react-router';
import ThemeToggle from './ThemeToggle';

export default function NavBar() {
  const logout = () => {
    apiMutation('/users/logout', {}, { method : 'POST' }).finally(() => {
      // do a full reload to make sure window.init is updated
      window.location.href = '/';
    });
  };

  const {
    isAuthenticated, isImpersonated, user, isLoading,
  } = useAuth();
  const { granted : canAccessAdminPanel } = useGlobalPermission('CAN_ACCESS_ADMIN_PANEL');

  const location = useLocation();

  const defaultLinkClass = `
    h-full
    p-2
    px-3
    rounded
    hover:bg-(--gray-3)
    dark:hover:bg-(--gray-3)
    dark:hover:text-(--gray-12)
    text-(--gray-a11)
    dark:text-(--gray-a11)`;

  const activeLinkClass = `
    h-full
    p-2
    px-3
    rounded
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
    p-3
    right-0
    mt-2
    z-50
    max-w-[90vw]
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
    whitespace-nowrap
    rounded
    hover:bg-(--gray-3)
    dark:hover:bg-(--gray-3)
    dark:hover:text-(--gray-12)
    text-(--gray-a11)
    dark:text-(--gray-a11)
  `;

  return (
    <NavigationMenu.Root className="h-[var(--NavBarHeight)]">
      <NavigationMenu.List className="flex p-1 pr-4 dark:border-b-(--gray-a6) dark:border-b-1 shadow dark:shadow-none">
        <div className="flex">
          <NavLink to="/" className={location.pathname === '/' ? activeLinkClass : defaultLinkClass}>
            <NavigationMenu.Item>
              {isAuthenticated ? 'Dashboard' : 'Home'}
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

          {isAuthenticated && (
            <>
              <NavLink to="/support" className={location.pathname === '/support' ? activeLinkClass : defaultLinkClass}>
                <NavigationMenu.Item>
                  Support
                </NavigationMenu.Item>
              </NavLink>
              <NotificationsPopover
                triggerClassName={defaultLinkClass}
                contentClassName={contentBase}
              />
            </>
          )}

          <ThemeToggle
            triggerClassName={defaultLinkClass}
            contentClassName={contentBase}
            contentItemClassName={contentItem}
          />

          {isAuthenticated ? (
            <NavigationMenu.Item className="relative">
              <NavigationMenu.Trigger
                className={defaultLinkClass}
                onPointerMove={(event) => event.preventDefault()}
                onPointerLeave={(event) => event.preventDefault()}
              >
                <Text
                  color={isImpersonated ? COLOR_HINT : undefined}
                  className={isImpersonated ? 'animate-pulse' : undefined}
                >
                  <Flex direction="row" align="center" gap="1">
                    {isImpersonated ? <ImpersonateIcon className="inline" /> : <TbUserCircle className="inline" aria-label="Current user" />}
                    {/* Show skeleton until we have auth state */}
                    <Skeleton loading={isLoading}>
                      <Text>
                        {isImpersonated ? 'Impersonating ' : ''}
                        {user?.name || 'Unknown'}
                      </Text>
                    </Skeleton>
                  </Flex>
                </Text>
              </NavigationMenu.Trigger>
              <NavigationMenu.Content
                className={contentBase}
                onPointerEnter={(event) => event.preventDefault()}
                onPointerLeave={(event) => event.preventDefault()}
              >
                <ul className="grid gap-2">
                  <li>
                    <NavLink
                      to="/profile"
                      className={contentItem}
                    >
                      Profile
                    </NavLink>
                  </li>

                  {canAccessAdminPanel && (
                    <li>
                      <NavLink
                        to="/admin"
                        className={contentItem}
                      >
                        Admin Portal
                      </NavLink>
                    </li>
                  )}
                  {isImpersonated && (
                    <li>
                      <button
                        type="button"
                        onClick={stopImpersonation}
                        className={contentItem}
                      >
                        Stop Impersonating
                      </button>
                    </li>
                  )}
                  <li>
                    <button
                      type="button"
                      onClick={logout}
                      className={contentItem}
                    >
                      Log Out
                    </button>
                  </li>
                </ul>
              </NavigationMenu.Content>
            </NavigationMenu.Item>
          ) : (
            <NavLink to="/login" className={location.pathname === '/login' ? activeLinkClass : defaultLinkClass}>
              <NavigationMenu.Item>
                <Flex direction="row" align="center" gap="1">
                  <TbUserCircle className="inline" />
                  Log In
                </Flex>
              </NavigationMenu.Item>
            </NavLink>
          )}
        </div>
        <NavigationMenu.Indicator />
      </NavigationMenu.List>
    </NavigationMenu.Root>
  );
}
