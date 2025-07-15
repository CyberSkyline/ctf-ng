import { updateEvent } from '@/hooks/events';
import { Button, Flex, Heading } from '@radix-ui/themes';
import { Link } from 'react-router';
import AdminSidebar from 'components/AdminSidebar';
import type { Event } from '@/types';
import { useState } from 'react';
import { TeamIcon, UserIcon } from '@/constants';
import AdminChallengeCard from './AdminChallengeCard';
import EventDataForm from './EventDataForm';

export default function EventSidebar({ entity }: { entity: Event }) {
  const [ formError, setFormError ] = useState<string|undefined>();
  return (
    <AdminSidebar title="Event Details">

      <EventDataForm
        initial={entity}
        onSubmit={
          (e) => {
            updateEvent(entity.id, e).then(() => {
              setFormError(undefined);
            }).catch((err) => {
              setFormError(err.message);
            });
          }
        }
        error={formError}
      />

      <Flex direction="row" gap="4" className="*:!grow w-full">
        <Button variant="soft" asChild>
          <Link to={`/admin/teams?event=${entity.id}`}>
            <TeamIcon />
            Teams
          </Link>
        </Button>
        <Button variant="soft" asChild>
          <Link to={`/admin/users?event=${entity.id}`}>
            <UserIcon />
            Users
          </Link>
        </Button>
      </Flex>
      <Heading>Challenges</Heading>
      <AdminChallengeCard />

    </AdminSidebar>
  );
}
