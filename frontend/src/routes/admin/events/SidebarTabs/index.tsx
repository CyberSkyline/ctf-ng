import { DeploymentIcon, EventIcon, TeamIcon } from '@/constants';
import { TbStar } from 'react-icons/tb';
import type { AdminEvent } from '@/types';
import { Tabs } from '@radix-ui/themes';
import AdminLink from 'components/AdminLink';
import AdminSidebar from 'components/AdminSidebar';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import { useId } from 'react';
import { useSearchParams } from 'react-router';
import EventChallengesTab from './EventChallengesTab';
import EventDetailsTab from './EventDetailsTab';
import EventFeedbackTab from './EventFeedbackTab';
import EventGameplayTab from './EventGameplayTab';
import EventRegistrationTab from './EventRegistrationTab';

export default function EventSidebar({ entity }: { entity: AdminEvent }) {
  const [ searchParams, setSearchParams ] = useSearchParams();
  const headerId = useId();

  return (
    <AdminSidebar labelId={headerId}>
      <AdminSidebarHeader title={entity.name} icon={<EventIcon />} id={headerId}>
        <AdminLink
          to={`/events/${entity.id}?tab=leaderboard`}
          icon={TbStar}
          label="Leaderboard"
        />
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
          <Tabs.Trigger value="registration">
            Registration
          </Tabs.Trigger>
          <Tabs.Trigger value="gameplay">
            Gameplay
          </Tabs.Trigger>
          <Tabs.Trigger value="challenges">
            Challenges
          </Tabs.Trigger>
          <Tabs.Trigger value="feedback">
            Feedback
          </Tabs.Trigger>
        </Tabs.List>
        <Tabs.Content value="details">
          <EventDetailsTab event={entity} />
        </Tabs.Content>
        <Tabs.Content value="registration">
          <EventRegistrationTab event={entity} />
        </Tabs.Content>
        <Tabs.Content value="gameplay">
          <EventGameplayTab event={entity} />
        </Tabs.Content>
        <Tabs.Content value="challenges">
          <EventChallengesTab event={entity} />
        </Tabs.Content>
        <Tabs.Content value="feedback" className="flex-grow">
          <EventFeedbackTab event={entity} />
        </Tabs.Content>
      </Tabs.Root>
    </AdminSidebar>
  );
}
