import {
  COLOR_INFO,
  DeploymentIcon,
  EventIcon,
  TeamIcon,
} from '@/constants';
import { useAdminEventChallenges } from '@/hooks/challenge';
import type { Event } from '@/types';
import { Button } from '@radix-ui/themes';
import AdminSidebar from 'components/AdminSidebar';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import { ErrorCallout } from 'components/Callouts';
import EventHeader from 'components/EventHeader';
import { Link } from 'react-router';
import AdminChallengeCard from './AdminChallengeCard';
import ChallengeUploadModal from './ChallengeUploadModal';
import EventModal from './EventModal';

export default function EventSidebar({ entity }: { entity: Event }) {
  const { data : challenges, error } = useAdminEventChallenges(entity.id);

  return (
    <AdminSidebar>
      <AdminSidebarHeader title={entity.name} icon={<EventIcon />}>
        <Button variant="soft" color={COLOR_INFO} asChild>
          <Link to={`/admin/deployments?filter=${btoa(JSON.stringify({ event_name : { filterType : 'text', type : 'equals', filter : entity.name } }))}`}>
            <DeploymentIcon />
            Deployments
          </Link>
        </Button>
        <Button variant="soft" color={COLOR_INFO} asChild>
          <Link to={`/admin/teams?filter=${btoa(JSON.stringify({ event_name : { filterType : 'text', type : 'equals', filter : entity.name } }))}`}>
            <TeamIcon />
            Teams
          </Link>
        </Button>
        <EventModal eventToUpdate={entity} />
      </AdminSidebarHeader>

      <EventHeader
        event={entity}
      />

      <AdminSidebarHeader title="Challenges">
        <ChallengeUploadModal eventId={entity.id} />
      </AdminSidebarHeader>

      {error && <ErrorCallout>{error.message}</ErrorCallout>}

      {challenges && challenges.length > 0 && (
        challenges.map((challenge) => (
          <AdminChallengeCard key={challenge.id} challenge={challenge} />
        ))
      )}
    </AdminSidebar>
  );
}
