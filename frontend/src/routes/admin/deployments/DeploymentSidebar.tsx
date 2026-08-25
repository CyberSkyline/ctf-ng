import {
  ChallengeIcon,
  DeploymentIcon,
  EventIcon,
  TeamIcon,
} from '@/constants';
import { useDeployment, useDeploymentServices, useDeploymentVariables } from '@/hooks/container';
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

export default function DeploymentSidebar({ selectedId }: { selectedId: number }) {
  const { data : deployment, error : deploymentError, isLoading : deploymentLoading } = useDeployment(selectedId);
  const { data : serviceData, error } = useDeploymentServices(deployment?.challenge_id ?? null, deployment?.team_id ?? null);
  const { data : variables, error : varsError } = useDeploymentVariables(deployment?.challenge_id ?? null, deployment?.team_id ?? null);
  const headerId = useId();

  if (deploymentError) {
    return (
      <AdminSidebar labelId={headerId}>
        <ErrorCallout>{deploymentError.message}</ErrorCallout>
      </AdminSidebar>
    );
  }

  return (
    <AdminSidebar labelId={headerId}>
      <AdminSidebarHeader
        title={deployment ? `${deployment.challenge_name} - ${deployment.team_name}` : 'Loading'}
        icon={<DeploymentIcon />}
        id={headerId}
        loading={deploymentLoading}
      >
        {deployment && (
          <>
            <AdminLink
              to="/admin/challenges"
              id={deployment.challenge_id}
              icon={ChallengeIcon}
              label="Challenge"
            />
            <AdminLink
              to="/admin/teams"
              id={deployment.team_id}
              icon={TeamIcon}
              label="Team"
            />
            <AdminLink
              to="/admin/events"
              id={deployment.event_id}
              icon={EventIcon}
              label="Event"
            />
          </>
        )}
      </AdminSidebarHeader>

      <AdminSidebarHeader title="Services" />
      {deployment && (
        <>
          <RecycleDeploymentModal challengeId={deployment.challenge_id} teamId={deployment.team_id} />
          <DeleteDeploymentModal challengeId={deployment.challenge_id} teamId={deployment.team_id} />
          <ConnectDeploymentModal challengeId={deployment.challenge_id} teamId={deployment.team_id} />
        </>
      )}
      {error && <ErrorCallout>{error.message}</ErrorCallout>}
      <Skeleton loading={!serviceData} className="min-h-48">
        <Grid columns="2" gap="2">
          { serviceData?.map((service) => (
            <ServiceCard key={service.id} service={service} />
          )) }
        </Grid>
      </Skeleton>

      <AdminSidebarHeader title="Variables" />
      {varsError && <ErrorCallout>{varsError.message}</ErrorCallout> }
      <Skeleton loading={!variables} className="min-h-24">
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
      </Skeleton>
    </AdminSidebar>
  );
}
