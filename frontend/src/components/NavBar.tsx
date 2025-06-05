import { NavigationMenu } from 'radix-ui';
import { DropdownMenu } from '@radix-ui/themes';
import { NavLink } from 'react-router';
import { ROUTEPREFIX } from '../constants';

export default function NavBar() {
  return (
    <NavigationMenu.Root className="h-[var(--NavBarHeight)]">
      <NavigationMenu.List className="flex p-1 shadow-md pr-4">
        <div className="flex">
          <NavigationMenu.Item className="p-2">
            <NavLink to={`/${ROUTEPREFIX}`}>
              Dashboard
            </NavLink>
          </NavigationMenu.Item>
          <NavigationMenu.Item className="p-2">
            <NavLink to={`/${ROUTEPREFIX}/events`}>
              Events*
            </NavLink>
          </NavigationMenu.Item>
          <NavigationMenu.Item className="p-2">
            <NavLink to={`/${ROUTEPREFIX}`}>
              Practice*
            </NavLink>
          </NavigationMenu.Item>
        </div>
        <div className="flex ml-auto">
          <NavigationMenu.Item className="p-2">
            <NavLink to={`/${ROUTEPREFIX}/support`}>
              Support
            </NavLink>
          </NavigationMenu.Item>
          <NavigationMenu.Item className="p-2">
            <NavLink to={`/${ROUTEPREFIX}`}>
              Notifications*
            </NavLink>
          </NavigationMenu.Item>

          <DropdownMenu.Root>
            <DropdownMenu.Trigger>
              <button type="button" className="p-2">
                Profile
              </button>
            </DropdownMenu.Trigger>
            <DropdownMenu.Content
              className="mt-2 rounded-md shadow-lg p-2 border"
            >
              <DropdownMenu.Item asChild>
                <NavLink
                  to={`/${ROUTEPREFIX}/profile`}
                  className="flex items-center gap-2 px-2 py-1.5 rounded"
                >
                  Profile
                </NavLink>
              </DropdownMenu.Item>

              <DropdownMenu.Item asChild>
                <NavLink
                  to={`/${ROUTEPREFIX}/admin`}
                  className="flex items-center gap-2 px-2 py-1.5 rounded"
                >
                  Admin Portal
                </NavLink>
              </DropdownMenu.Item>
              <DropdownMenu.Separator className="h-px bg-gray-200 my-1" />
              <DropdownMenu.Item asChild>
                <button
                  type="button"
                  onClick={() => alert('Logged out')}
                  className="w-full flex items-center gap-2 px-2 py-1.5 rounded"
                >
                  Log Out
                </button>
              </DropdownMenu.Item>
            </DropdownMenu.Content>
          </DropdownMenu.Root>
        </div>
      </NavigationMenu.List>
    </NavigationMenu.Root>
  );
}
