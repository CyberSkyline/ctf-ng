import {
  AnnouncementIcon,
  ChallengeIcon,
  DeploymentIcon,
  EventIcon,
  TeamIcon,
  UserIcon,
} from '@/constants';
import { useGlobalPermission } from '@/hooks/permissions';
import { Card, Flex, Skeleton } from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import { NavigationMenu } from 'radix-ui';
import type { IconType } from 'react-icons';
import {
  TbBraces,
  TbChartPie,
  TbLayoutDashboard,
  TbMessage,
  TbSettings,
  TbTags,
  TbHeartHandshake,
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
            [&[aria-current='page']]:bg-[var(--accent-9)]
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
  const { denied, isLoading } = useGlobalPermission('CAN_ACCESS_ADMIN_PANEL');

  if (denied) {
    return <ErrorCallout>You do not have permission to access this page.</ErrorCallout>;
  }

  return (
    <Flex direction="row" className="absolute inset-0 overflow-hidden">
      <div className="flex-shrink-0 h-full p-3 pr-0">
        {isLoading
          ? <Skeleton className="!h-full w-48" />
          : (
            <Card className="h-full w-48">
              <NavigationMenu.Root orientation="vertical" aria-label="Sidebar" className="h-full overflow-y-auto">
                <NavigationMenu.List>
                  <NavItem to="/admin" label="Dashboard" icon={TbLayoutDashboard} />
                  <NavItem to="/admin/reports" label="Reports" icon={TbChartPie} />
                  <NavItem to="/admin/sponsors" label="Sponsors" icon={TbHeartHandshake} />
                  <NavItem to="/admin/events" label="Events" icon={EventIcon} />
                  <NavItem to="/admin/users" label="Users" icon={UserIcon} />
                  <NavItem to="/admin/teams" label="Teams" icon={TeamIcon} />
                  <NavItem to="/admin/challenges" label="Challenges" icon={ChallengeIcon} />
                  <NavItem to="/admin/deployments" label="Deployments" icon={DeploymentIcon} />
                  <NavItem to="/admin/announcements" label="Announcements" icon={AnnouncementIcon} />
                  <NavItem to="/admin/tickets" label="Tickets" icon={TbMessage} />
                  <NavItem to="/admin/tags" label="Tags" icon={TbTags} />
                  <NavItem to="/admin/settings" label="Settings" icon={TbSettings} />
                  <NavItem to="/admin/api-test" label="API Test" icon={TbBraces} />
                </NavigationMenu.List>
              </NavigationMenu.Root>
            </Card>
          )}
      </div>
      <main className="flex-grow overflow-y-auto p-3">
        {isLoading ? <Skeleton className="!h-full" /> : <Outlet />}
      </main>
    </Flex>
  );
}
