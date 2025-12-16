import { useAdminEventChallenges } from '@/hooks/challenge';
import type { Event } from '@/types';
import { Flex } from '@radix-ui/themes';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import { ErrorCallout } from 'components/Callouts';
import AdminChallengeCard from '../AdminChallengeCard';
import ChallengeUploadModal from '../ChallengeUploadModal';

export default function EventChallengesTab({ event }: {event: Event}) {
  const { data : challenges, error } = useAdminEventChallenges(event.id);

  return (
    <Flex direction="column" gap="3">
      <AdminSidebarHeader title="Challenges">
        <ChallengeUploadModal eventId={event.id} />
      </AdminSidebarHeader>

      {error && <ErrorCallout>{error.message}</ErrorCallout>}

      {challenges && challenges.length > 0 && (
        challenges.map((challenge) => (
          <AdminChallengeCard key={challenge.id} challenge={challenge} />
        ))
      )}
    </Flex>
  );
}
