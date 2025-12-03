import { DeploymentIcon, EventIcon } from '@/constants';
import type { Challenge } from '@/types';
import { Tabs } from '@radix-ui/themes';
import AdminLink from 'components/AdminLink';
import AdminSidebar from 'components/AdminSidebar';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import ChallengeIcon from 'components/ChallengeIcon';
import { useId } from 'react';
import { useSearchParams } from 'react-router';
import ChallengeDownloadButton from './ChallengeDownloadButton';
import ChallengeUpdateModal from './ChallengeUpdateModal';
import ChallengeAttemptsTab from './SidebarTabs/ChallengeAttemptsTab';
import ChallengeBlueprintTab from './SidebarTabs/ChallengeBlueprintTab';
import ChallengeDetailsTab from './SidebarTabs/ChallengeDetailsTab';

export default function ChallengeSidebar({ entity }: {entity: Challenge}) {
  const [ searchParams, setSearchParams ] = useSearchParams();
  const headerId = useId();

  return (
    <AdminSidebar labelId={headerId}>
      <AdminSidebarHeader title={entity.name} icon={<ChallengeIcon icon={entity.icon} />} id={headerId}>
        <AdminLink
          to="/admin/events"
          id={entity.event_id}
          icon={EventIcon}
          label="Event"
        />
        <AdminLink
          to="/admin/deployments"
          filter={{
            challenge_name : { filterType : 'text', type : 'equals', filter : entity.name },
            event_name : { filterType : 'text', type : 'equals', filter : entity.event_name },
          }}
          icon={DeploymentIcon}
          label="Deployments"
        />
        <ChallengeUpdateModal challengeId={entity.id} />
        <ChallengeDownloadButton challenge={entity} />
      </AdminSidebarHeader>

      <Tabs.Root
        className="h-full flex flex-col"
        value={searchParams.get('tab') || 'details'}
        onValueChange={
          (value) => {
            if (value === searchParams.get('tab')) return;
            setSearchParams((prev) => {
              prev.set('tab', value);
              return prev;
            });
          }
        }
        activationMode="manual"
      >
        <Tabs.List className="mb-3 shrink-0">
          <Tabs.Trigger value="details">
            Details
          </Tabs.Trigger>
          <Tabs.Trigger value="blueprint">
            Blueprint
          </Tabs.Trigger>
          <Tabs.Trigger value="attempts">
            Attempts
          </Tabs.Trigger>
        </Tabs.List>
        <Tabs.Content value="details" className="flex flex-col gap-3 pb-3">
          <ChallengeDetailsTab challenge={entity} />
        </Tabs.Content>
        <Tabs.Content value="blueprint" className="pb-3">
          <ChallengeBlueprintTab challengeId={entity.id} />
        </Tabs.Content>
        <Tabs.Content value="attempts" className="flex flex-col flex-grow">
          <ChallengeAttemptsTab challengeId={entity.id} />
        </Tabs.Content>
      </Tabs.Root>
    </AdminSidebar>
  );
}
