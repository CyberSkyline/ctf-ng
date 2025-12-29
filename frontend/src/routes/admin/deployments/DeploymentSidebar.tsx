import {
  ChallengeIcon,
  DeploymentIcon,
  EventIcon,
  TeamIcon,
} from '@/constants';
import { useDeploymentServices, useDeploymentVariables } from '@/hooks/container';
import type { Deployment } from '@/types';
import { Grid, Skeleton, Table } from '@radix-ui/themes';
import AdminLink from 'components/AdminLink';
import AdminSidebar from 'components/AdminSidebar';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import { ErrorCallout, InfoCallout } from 'components/Callouts';
import { useId } from 'react';
import { TbVariable } from 'react-icons/tb';
import ServiceCard from './ServiceCard';
import RecycleDeploymentModal from './RecycleDeploymentModal';
import DeleteDeploymentModal from './DeleteDeploymentModal';
import ConnectDeploymentModal from './ConnectDeploymentModal';

export default function DeploymentSidebar({ entity }: {entity: Deployment}) {
  const { data : serviceData, error } = useDeploymentServices(entity.challenge_id, entity.team_id);
  const { data : variables, error : varsError } = useDeploymentVariables(entity.challenge_id, entity.team_id);
  const headerId = useId();

  return (
    <AdminSidebar labelId={headerId}>
      <AdminSidebarHeader
        title={`${entity.challenge_name} - ${entity.team_name}`}
        icon={<DeploymentIcon />}
        id={headerId}
      >
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
      <RecycleDeploymentModal challengeId={entity.challenge_id} teamId={entity.team_id} />
      <DeleteDeploymentModal challengeId={entity.challenge_id} teamId={entity.team_id} />
      <ConnectDeploymentModal challengeId={entity.challenge_id} teamId={entity.team_id} />
      {error && <ErrorCallout>{error.message}</ErrorCallout>}
      <Skeleton loading={!serviceData}>
        <Grid columns="2" gap="2">
          { serviceData?.map((service) => (
            <ServiceCard key={service.id} service={service} />
          )) }
        </Grid>
      </Skeleton>

      <AdminSidebarHeader title="Variables" />
      {varsError && <ErrorCallout>{varsError.message}</ErrorCallout> }
      {variables && Object.keys(variables).length === 0 && <InfoCallout>This challenge does not have any variables.</InfoCallout>}
      {variables && Object.keys(variables).length > 0
      && (
        <Table.Root>
          <Table.Header>
            <Table.ColumnHeaderCell>Name</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Value</Table.ColumnHeaderCell>
          </Table.Header>
          <Table.Body>
            {Object.entries(variables || {}).map(([ key, value ]) => (
              <Table.Row key={key}>
                <Table.Cell>
                  <TbVariable className="inline me-1 opacity-50" aria-label="Variable" />
                  {key}
                </Table.Cell>
                <Table.Cell>{value as string}</Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table.Root>
      )}
    </AdminSidebar>
  );
}
