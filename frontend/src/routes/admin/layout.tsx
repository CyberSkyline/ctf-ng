import { EventIcon, TeamIcon, UserIcon } from '@/constants';
import { Card, Flex } from '@radix-ui/themes';
import { NavigationMenu } from 'radix-ui';
import type { IconType } from 'react-icons';
import {
  TbBell, TbChartPie, TbLayoutDashboard, TbMessage,
  TbPackages, TbSettings,
} from 'react-icons/tb';
import { NavLink, Outlet } from 'react-router';

/**
 * Navigation item for the admin sidebar.
 */
function NavItem({
  to,
  label,
  icon : Icon = undefined,
}: {
    to: string;
    label: string;
    icon?: IconType
}) {
  return (
    <NavigationMenu.Item>
      <NavigationMenu.Link asChild>
        <NavLink
          to={to}
          end
          className="
            flex items-center gap-2
            [&[aria-current='page']]:bg-[var(--lime-9)]
            [&[aria-current='page']]:text-[var(--accent-contrast)]
            p-2 rounded overflow-hidden
          "
        >
          {Icon && <Icon className="text-xl shrink-0" />}
          <span>{label}</span>
        </NavLink>
      </NavigationMenu.Link>
    </NavigationMenu.Item>
  );
}

/**
 * Shared layout for all admin pages with sidebar navigation menu.
 * Individual page components are mounted at the <Outlet />.
 * Pages that exceed viewport height will scroll within the outlet.
 */
export default function AdminLayout() {
  return (
    <Flex direction="row" className="absolute top-0 bottom-0 left-0 right-0">
      <div className="flex-shrink-0 h-full p-4 pr-0">
        <Card asChild className="h-full w-48 overflow-hidden">
          <NavigationMenu.Root orientation="vertical" aria-label="Sidebar">
            <NavigationMenu.List>
              <NavItem to="/admin" label="Dashboard" icon={TbLayoutDashboard} />
              <NavItem to="/admin/reports" label="Reports" icon={TbChartPie} />
              <NavItem to="/admin/events" label="Events" icon={EventIcon} />
              <NavItem to="/admin/containers" label="Containers" icon={TbPackages} />
              <NavItem to="/admin/users" label="Users" icon={UserIcon} />
              <NavItem to="/admin/teams" label="Teams" icon={TeamIcon} />
              <NavItem to="/admin/notifications" label="Notifications" icon={TbBell} />
              <NavItem to="/admin/tickets" label="Tickets" icon={TbMessage} />
              <NavItem to="/admin/settings" label="Settings" icon={TbSettings} />
            </NavigationMenu.List>
          </NavigationMenu.Root>
        </Card>
      </div>
      <main className="flex-grow overflow-y-auto p-4">
        <Outlet />
      </main>
    </Flex>
  );
}
