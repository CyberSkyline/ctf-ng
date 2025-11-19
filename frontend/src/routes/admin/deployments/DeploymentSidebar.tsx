import {
  ChallengeIcon,
  DeploymentIcon,
  EventIcon,
  TeamIcon,
} from '@/constants';
import { useDeploymentServices } from '@/hooks/container';
import type { Deployment } from '@/types';
import { Grid, Skeleton } from '@radix-ui/themes';
import AdminLink from 'components/AdminLink';
import AdminSidebar from 'components/AdminSidebar';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import { ErrorCallout } from 'components/Callouts';
import ServiceCard from './ServiceCard';

export default function DeploymentSidebar({ entity }: {entity: Deployment}) {
  const { data : serviceData, error } = useDeploymentServices(entity.challenge_id, entity.team_id);

  return (
    <AdminSidebar>
      <AdminSidebarHeader title={`${entity.challenge_name} - ${entity.team_name}`} icon={<DeploymentIcon />}>
        <AdminLink
          to="/admin/challenges"
          id={entity.challenge_id}
          icon={ChallengeIcon}
          label="Challenge"
        />
        <AdminLink
          to="/admin/teams"
          id={entity.team_id}
          icon={TeamIcon}
          label="Team"
        />
        <AdminLink
          to="/admin/events"
          id={entity.event_id}
          icon={EventIcon}
          label="Event"
        />
      </AdminSidebarHeader>

      <AdminSidebarHeader title="Services" />
      {error && <ErrorCallout>{error.message}</ErrorCallout>}
      <Skeleton loading={!serviceData}>
        <Grid columns="2">
          { serviceData?.map((service) => (
            <ServiceCard key={service.id} service={service} />
          )) }
        </Grid>
      </Skeleton>
    </AdminSidebar>
  );
}
