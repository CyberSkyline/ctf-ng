import NotFound from 'components/NotFound';
import { useRoutes } from 'react-router';

import Dashboard from 'routes/dashboard';
import Notifications from 'routes/notifications';
import Profile from 'routes/profile';

// Support tickets
import Support from 'routes/support';
import CreateTicket from 'routes/support/CreateTicket';
import TicketDetail from 'routes/support/Detail';

// events
import Challenge from 'routes/events/challenge';
import Overview from 'routes/events/Overview';

// Admin Section
import AdminApiTest from 'routes/admin/api-test';
import AdminContainers from 'routes/admin/containers';
import AdminDashboard from 'routes/admin/dashboard';
import AdminEvents from 'routes/admin/events';
import AdminLayout from 'routes/admin/layout';
import AdminNotifications from 'routes/admin/notifications';
import AdminReports from 'routes/admin/reports';
import AdminSettings from 'routes/admin/settings';
import AdminTeams from 'routes/admin/teams';
import AdminTickets from 'routes/admin/tickets';
import AdminUsers from 'routes/admin/users';
import AvailableEvents from 'routes/events/AvailableEvents';

function Routes() {
  const routes = useRoutes([
    {
      path : '*',
      element : <NotFound />, // Catch-all route for 404 page
    },
    { path : '/', element : <Dashboard /> },
    { path : '/events', element : <AvailableEvents /> },
    {
      path : '/events/:idEvent',
      children : [
        { index : true, element : <Overview /> },
        { path : 'challenge/:idChallenge', element : <Challenge /> },
      ],
    },
    { path : '/notifications/:idNotif', element : <Notifications /> },
    { path : '/profile', element : <Profile /> },
    {
      path : '/support',
      children : [
        { index : true, element : <Support /> },
        { path : 'createTicket', element : <CreateTicket /> },
        { path : ':idTicket', element : <TicketDetail /> },
      ],
    },
    {
      path : '/admin',
      element : <AdminLayout />,
      children : [
        { path : '*', element : <NotFound /> }, // Catch-all for admin routes
        { index : true, element : <AdminDashboard /> },
        { path : 'reports', element : <AdminReports /> },
        { path : 'events', element : <AdminEvents /> },
        { path : 'containers', element : <AdminContainers /> },
        { path : 'users', element : <AdminUsers /> },
        { path : 'teams', element : <AdminTeams /> },
        { path : 'notifications', element : <AdminNotifications /> },
        { path : 'tickets', element : <AdminTickets /> },
        { path : 'settings', element : <AdminSettings /> },
        { path : 'api-test', element : <AdminApiTest /> },
      ],
    },
  ]);

  return (
    <div className="p-4 min-h-[calc(100vh-var(--NavBarHeight)-var(--FooterBarHeight))] relative">
      {routes}
    </div>
  );
}

export default Routes;
