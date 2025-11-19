import {
  ChallengeIcon,
  COLOR_INFO,
  DeploymentIcon,
  EventIcon,
  TeamIcon,
} from '@/constants';
import { useDeploymentServices } from '@/hooks/container';
import type { Deployment } from '@/types';
import { Button, Grid, Skeleton } from '@radix-ui/themes';
import AdminSidebar from 'components/AdminSidebar';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import { ErrorCallout } from 'components/Callouts';
import { Link } from 'react-router';
import ServiceCard from './ServiceCard';

export default function DeploymentSidebar({ entity }: {entity: Deployment}) {
  const { data : serviceData, error } = useDeploymentServices(entity.challenge_id, entity.team_id);

  return (
    <AdminSidebar>
      <AdminSidebarHeader title={`${entity.challenge_name} - ${entity.team_name}`} icon={<DeploymentIcon />}>
        <Button variant="soft" color={COLOR_INFO} asChild>
          <Link to={`/admin/challenges?id=${entity.id}`}>
            <ChallengeIcon />
            Challenge
          </Link>
        </Button>
        <Button variant="soft" color={COLOR_INFO} asChild>
          <Link to={`/admin/teams?id=${entity.team_id}`}>
            <TeamIcon />
            Team
          </Link>
        </Button>
        <Button variant="soft" color={COLOR_INFO} asChild>
          <Link to={`/admin/events?id=${entity.event_id}`}>
            <EventIcon />
            Event
          </Link>
        </Button>
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
