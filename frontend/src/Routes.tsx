import { useRoutes } from 'react-router';
import NotFound from 'components/NotFound';

import Dashboard from 'routes/dashboard';
import Notifications from 'routes/notifications';
import Profile from 'routes/profile';
import Scoreboard from 'routes/scoreboard';
import Support from 'routes/support';

// events
import Overview from 'routes/events/Overview';
import Registration from 'routes/events/Registration';
import Challenge from 'routes/events/Challenge';

// Admin Section
import AdminDashboard from 'routes/admin/dashboard';
import AdminNotifications from 'routes/admin/notifications';
import AdminUsers from 'routes/admin/users';
import AdminTickets from 'routes/admin/tickets';

function Routes() {
  const prefix = 'hello';
  const routes = useRoutes([
    {
      path: '*',
      element: <NotFound />, // Catch-all route for 404 page
    },
    { path: `/${prefix}`, element: <Dashboard /> },
    {
      path: `/${prefix}/events/:idEvent`,
      children: [
        { index: true, element: <Overview /> },
        { path: 'registration', element: <Registration /> },
        { path: 'challenge/:idChallenge', element: <Challenge /> },
      ],
    },
    { path: `/${prefix}/notifications/:idNotif`, element: <Notifications /> },
    { path: `/${prefix}/profile`, element: <Profile /> },
    { path: `/${prefix}/scoreboard/:idEvent`, element: <Scoreboard /> },
    { path: `/${prefix}/support`, element: <Support /> },

    {
      path: `/${prefix}/admin`,
      children: [
        { path: 'dashboard', element: <AdminDashboard /> },
        { path: 'notifications', element: <AdminNotifications /> },
        { path: 'users', element: <AdminUsers /> },
        { path: 'tickets', element: <AdminTickets /> },
      ],
    },

  ]);

  return routes;
}

export default Routes;
