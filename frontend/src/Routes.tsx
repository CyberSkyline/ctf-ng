import { useState } from 'react';
import { useLocation, useRoutes } from 'react-router';

import ErrorPage from 'components/ErrorPage';
import NotFound from 'components/NotFound';
import Dashboard from 'routes/dashboard';
import Landing from 'routes/dashboard/Landing';
import Profile from 'routes/profile';

import RequireUser from 'components/RequireUser';
import Login from 'routes/login';

// Support tickets
import Support from 'routes/support';
import CreateTicket from 'routes/support/CreateTicket';
import TicketDetail from 'routes/support/Detail';

// events
import AvailableEvents from 'routes/events/AvailableEvents';

import Overview from 'routes/events/Overview';
import Challenge from 'routes/events/challenge';

// Practice area
import Practice from 'routes/practice';

// FAQ
import FAQPage from 'routes/faq';

// Admin Section
import AdminAnnouncements from 'routes/admin/announcements';
import AdminApiTest from 'routes/admin/api-test';
import AdminChallenges from 'routes/admin/challenges';
import AdminDashboard from 'routes/admin/dashboard';
import AdminDeployments from 'routes/admin/deployments';
import AdminEvents from 'routes/admin/events';
import AdminLayout from 'routes/admin/layout';
import AdminReports from 'routes/admin/reports';
import AdminSponsors from 'routes/admin/sponsors';
import AdminTags from 'routes/admin/tags';
import AdminTeams from 'routes/admin/teams';
import AdminTickets from 'routes/admin/tickets';
import AdminUsers from 'routes/admin/users';

function Routes() {
  const routes = useRoutes([
    {
      path : '*',
      element : <NotFound />, // Catch-all route for 404 page
    },
    { path : '/', element : <RequireUser replace={<Landing />}><Dashboard /></RequireUser> },
    { path : '/login', element : <Login /> },
    {
      path : '/events',
      element : <AvailableEvents />,
    },
    {
      path : '/events/:idEvent',
      children : [
        { index : true, element : <Overview /> },
        { path : 'invitecode/:inviteCode', element : <RequireUser><Overview /></RequireUser> },
        { path : 'challenge/:idChallenge', element : <RequireUser><Challenge /></RequireUser> },
      ],
    },
    {
      path : '/practice',
      element : <Practice />,
    },
    { path : '/profile', element : <RequireUser><Profile /></RequireUser> },
    {
      path : '/support',
      children : [
        { index : true, element : <RequireUser><Support /></RequireUser> },
        { path : 'createTicket', element : <RequireUser><CreateTicket /></RequireUser> },
        { path : ':idTicket', element : <RequireUser><TicketDetail /></RequireUser> },
      ],
    },
    {
      path : '/faq',
      element : <FAQPage />,
    },
    {
      path : '/admin',
      element : <RequireUser><AdminLayout /></RequireUser>,
      children : [
        { path : '*', element : <NotFound /> }, // Catch-all for admin routes
        { index : true, element : <AdminDashboard /> },
        { path : 'reports', element : <AdminReports /> },
        { path : 'sponsors', element : <AdminSponsors /> },
        { path : 'events', element : <AdminEvents /> },
        { path : 'users', element : <AdminUsers /> },
        { path : 'teams', element : <AdminTeams /> },
        { path : 'challenges', element : <AdminChallenges /> },
        { path : 'deployments', element : <AdminDeployments /> },
        { path : 'announcements', element : <AdminAnnouncements /> },
        { path : 'tickets', element : <AdminTickets /> },
        { path : 'tags', element : <AdminTags /> },
        { path : 'api-test', element : <AdminApiTest /> },
      ],
    },
  ]);

  const location = useLocation();

  // The server attaches errors to window.init for the one URL it rendered them
  // for. Remember that URL so navigating away - via the error page's own
  // actions or the nav bar - resumes normal routing instead of leaving the
  // error on screen.
  const [ errorPathname ] = useState(location.pathname);
  const error = location.pathname === errorPathname ? window.init.error : null;

  return (
    <div className="p-3 min-h-[calc(100vh-var(--NavBarHeight)-var(--FooterBarHeight))] relative mb-[var(--FooterBarHeight)]">
      {error ? <ErrorPage error={error} /> : routes}
    </div>
  );
}

export default Routes;
