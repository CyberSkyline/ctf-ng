import { COLOR_HINT, ImpersonateIcon, ROUTEPREFIX } from '@/constants';
import { apiMutation } from '@/fetchers';
import { useGlobalPermission } from '@/hooks/permissions';
import { stopImpersonation, useAuth } from '@/hooks/users';
import { Flex, Skeleton, Text } from '@radix-ui/themes';
import NotificationsPopover from 'components/NotificationsPopover';
import { NavigationMenu } from 'radix-ui';
import { TbMenu2, TbUserCircle } from 'react-icons/tb';
import { NavLink, useLocation } from 'react-router';
import { twMerge } from 'tailwind-merge';
import ThemeToggle from './ThemeToggle';

export default function NavBar() {
  const logout = () => {
    apiMutation('/users/logout', {}, { method : 'POST' }).finally(() => {
      // do a full reload to make sure window.init is updated
      window.location.href = `${ROUTEPREFIX}/`;
    });
  };

  const {
    isAuthenticated, isImpersonated, user, isLoading,
  } = useAuth();
  const { granted : canAccessAdminPanel } = useGlobalPermission('CAN_ACCESS_ADMIN_PANEL');

  const location = useLocation();

  const defaultLinkClass = `
    flex
    items-center
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
    flex
    items-center
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

  const linkClass = (path: string) => (location.pathname === path ? activeLinkClass : defaultLinkClass);

  // Account actions, shared by the user menu (wide screens) and the collapsed Menu (narrow screens).
  const accountItems = (
    <>
      <li>
        <NavigationMenu.Link asChild>
          <NavLink to="/profile" className={contentItem}>
            Profile
          </NavLink>
        </NavigationMenu.Link>
      </li>

      {canAccessAdminPanel && (
        <li>
          <NavigationMenu.Link asChild>
            <NavLink to="/admin" className={contentItem}>
              Admin Portal
            </NavLink>
          </NavigationMenu.Link>
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
    </>
  );

  const menuLink = (to: string, label: string) => (
    <li>
      <NavigationMenu.Link asChild>
        {/* NavLink sets aria-current="page" on the current route; mirror it visually. */}
        <NavLink to={to} className={twMerge(contentItem, 'aria-[current=page]:font-semibold aria-[current=page]:!text-(--gray-12)')}>
          {label}
        </NavLink>
      </NavigationMenu.Link>
    </li>
  );

  return (
    <NavigationMenu.Root className="h-[var(--NavBarHeight)]">
      {/* Every child of the list is a NavigationMenu.Item (<li>), with links inside items (WCAG 1.3.1). */}
      <NavigationMenu.List className="flex p-1 pr-4 dark:border-b-(--gray-a6) dark:border-b-1 shadow dark:shadow-none">
        {/* Below 640px the full row doesn't fit (WCAG 1.4.10), so page links and account actions collapse into this menu. */}
        <NavigationMenu.Item value="menu" className="relative sm:hidden">
          <NavigationMenu.Trigger
            className={twMerge(defaultLinkClass, 'gap-1.5')}
            onPointerMove={(event) => event.preventDefault()}
            onPointerLeave={(event) => event.preventDefault()}
          >
            <TbMenu2 aria-hidden="true" />
            Menu
          </NavigationMenu.Trigger>
          <NavigationMenu.Content
            className={twMerge(contentBase, 'left-0 right-auto min-w-52')}
            onPointerEnter={(event) => event.preventDefault()}
            onPointerLeave={(event) => event.preventDefault()}
          >
            <ul className="grid gap-2">
              {menuLink('/', isAuthenticated ? 'Dashboard' : 'Home')}
              {menuLink('/events', 'Events')}
              {menuLink('/practice', 'Practice')}
              {isAuthenticated && menuLink('/support', 'Support')}
              {isAuthenticated ? (
                <>
                  <li aria-hidden="true" className="border-t border-(--gray-a6)" />
                  {accountItems}
                </>
              ) : menuLink('/login', 'Log In')}
            </ul>
          </NavigationMenu.Content>
        </NavigationMenu.Item>

        <NavigationMenu.Item className="max-sm:hidden">
          <NavigationMenu.Link asChild>
            <NavLink to="/" className={linkClass('/')}>
              {isAuthenticated ? 'Dashboard' : 'Home'}
            </NavLink>
          </NavigationMenu.Link>
        </NavigationMenu.Item>
        <NavigationMenu.Item className="max-sm:hidden">
          <NavigationMenu.Link asChild>
            <NavLink to="/events" className={linkClass('/events')}>
              Events
            </NavLink>
          </NavigationMenu.Link>
        </NavigationMenu.Item>
        <NavigationMenu.Item className="max-sm:hidden">
          <NavigationMenu.Link asChild>
            <NavLink to="/practice" className={linkClass('/practice')}>
              Practice
            </NavLink>
          </NavigationMenu.Link>
        </NavigationMenu.Item>

        {/* The first right-hand item takes ml-auto to push the group right. */}
        {isAuthenticated && (
          <>
            <NavigationMenu.Item className="max-sm:hidden ml-auto">
              <NavigationMenu.Link asChild>
                <NavLink to="/support" className={linkClass('/support')}>
                  Support
                </NavLink>
              </NavigationMenu.Link>
            </NavigationMenu.Item>
            <NotificationsPopover
              itemClassName="max-sm:ml-auto"
              triggerClassName={defaultLinkClass}
              contentClassName={contentBase}
            />
          </>
        )}

        <ThemeToggle
          itemClassName={isAuthenticated ? undefined : 'ml-auto'}
          triggerClassName={defaultLinkClass}
          contentClassName={contentBase}
          contentItemClassName={contentItem}
        />

        {isAuthenticated ? (
          <NavigationMenu.Item className="relative max-sm:hidden">
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
            >
              <ul className="grid gap-2">
                {accountItems}
              </ul>
            </NavigationMenu.Content>
          </NavigationMenu.Item>
        ) : (
          <NavigationMenu.Item className="max-sm:hidden">
            <NavigationMenu.Link asChild>
              <NavLink to="/login" className={twMerge(linkClass('/login'), 'gap-1')}>
                <TbUserCircle className="inline" aria-hidden="true" />
                Log In
              </NavLink>
            </NavigationMenu.Link>
          </NavigationMenu.Item>
        )}
        <NavigationMenu.Indicator />
      </NavigationMenu.List>
    </NavigationMenu.Root>
  );
}
