import { TeamIcon } from '@/constants';
import { useEventChallenges } from '@/hooks/challenge';
import type { Event } from '@/types';
import { Button } from '@radix-ui/themes';
import AdminSidebar from 'components/AdminSidebar';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import EventHeader from 'components/EventHeader';
import { Link } from 'react-router';
import AdminChallengeCard from './AdminChallengeCard';
import ChallengeUploadModal from './ChallengeUploadModal';
import EventModal from './EventModal';

export default function EventSidebar({ entity }: { entity: Event }) {
const { data : challenges } = useEventChallenges(entity.id);

  return (
    <AdminSidebar>
      <AdminSidebarHeader title="Event Details">
        <Button variant="soft" color="jade" asChild>
          <Link to={`/admin/teams?event=${entity.id}`}>
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

      {challenges && challenges.length > 0 && (
        challenges.map((challenge) => (
          <AdminChallengeCard key={challenge.id} challenge={challenge} />
        ))
      )}
    </AdminSidebar>
  );
}
