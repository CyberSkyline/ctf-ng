import { DeploymentIcon, EventIcon, TeamIcon } from '@/constants';
import { useAdminEventChallenges } from '@/hooks/challenge';
import type { Event } from '@/types';
import AdminLink from 'components/AdminLink';
import AdminSidebar from 'components/AdminSidebar';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import { ErrorCallout } from 'components/Callouts';
import EventHeader from 'components/EventHeader';
import { useId } from 'react';
import AdminChallengeCard from './AdminChallengeCard';
import ChallengeUploadModal from './ChallengeUploadModal';
import EventModal from './EventModal';

export default function EventSidebar({ entity }: { entity: Event }) {
  const { data : challenges, error } = useAdminEventChallenges(entity.id);
  const headerId = useId();

  return (
    <AdminSidebar labelId={headerId}>
      <AdminSidebarHeader title={entity.name} icon={<EventIcon />} id={headerId}>
        <AdminLink
          to="/admin/deployments"
          filter={{ event_name : { filterType : 'text', type : 'equals', filter : entity.name } }}
          icon={DeploymentIcon}
          label="Deployments"
        />
        <AdminLink
          to="/admin/teams"
          filter={{ event_name : { filterType : 'text', type : 'equals', filter : entity.name } }}
          icon={TeamIcon}
          label="Teams"
        />
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
