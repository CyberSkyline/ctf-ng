import { TeamIcon } from '@/constants';
import type { Event } from '@/types';
import { Button } from '@radix-ui/themes';
import AdminSidebar from 'components/AdminSidebar';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import EventHeader from 'components/EventHeader';
import { Link } from 'react-router';
import EventModal from './EventModal';

export default function EventSidebar({ entity }: { entity: Event }) {
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

    </AdminSidebar>
  );
}
