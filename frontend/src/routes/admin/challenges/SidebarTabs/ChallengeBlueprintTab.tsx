import { COLOR_WARNING } from '@/constants';
import { apiMutation } from '@/fetchers';
import { useAdminChallengeBlueprints } from '@/hooks/challenge';
import {
  Button,
  Card,
  Code,
  DataList,
  Grid,
} from '@radix-ui/themes';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import { ErrorCallout, WarningCallout } from 'components/Callouts';
import ImagePullStatus from 'components/ImagePullStatus';
import Modal from 'components/Modal';
import { TbDownload, TbPackage } from 'react-icons/tb';

export default function ChallengeBlueprintTab({ challengeId }: {challengeId: number}) {
  const { data : blueprints, error } = useAdminChallengeBlueprints(challengeId);

  const handlePull = () => apiMutation(`/admin/challenges/${challengeId}/pull`, {}, {
    method : 'POST',
  });

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  return (
    <>
      <AdminSidebarHeader title="Containers">
        <Modal
          title="Pull Images"
          description="This will pull all container images used by this challenge.
          Existing deployments will need to be recycled to use updated images."
          trigger={(
            <Button variant="soft" color={COLOR_WARNING} disabled={!blueprints}>
              <TbDownload />
              Pull Images
            </Button>
          )}
          onSubmit={handlePull}
          submitVerb="Pull"
          submitColor={COLOR_WARNING}
        >
          <WarningCallout>
            This will affect all challenges using these images.
          </WarningCallout>
        </Modal>
      </AdminSidebarHeader>

      <Grid columns="2" gap="2" mt="2">
        {blueprints?.map((blueprint) => (
          <Card key={blueprint.id} className="mb-3">
            <AdminSidebarHeader title={blueprint.name} icon={<TbPackage />}>
              <ImagePullStatus id={blueprint.id} />
            </AdminSidebarHeader>
            <DataList.Root className="!gap-1 !mt-3">
              <DataList.Item>
                <DataList.Label>Image</DataList.Label>
                <DataList.Value>
                  {blueprint.image}
                </DataList.Value>
              </DataList.Item>
              <DataList.Item>
                <DataList.Label>Hostname</DataList.Label>
                <DataList.Value>
                  {blueprint.hostname}
                </DataList.Value>
              </DataList.Item>
              <DataList.Item>
                <DataList.Label>Command</DataList.Label>
                <DataList.Value>
                  {JSON.stringify(blueprint.command)}
                </DataList.Value>
              </DataList.Item>
              <DataList.Item>
                <DataList.Label>Entrypoint</DataList.Label>
                <DataList.Value>
                  {JSON.stringify(blueprint.entrypoint)}
                </DataList.Value>
              </DataList.Item>
              <DataList.Item>
                <DataList.Label>TTY</DataList.Label>
                <DataList.Value>
                  {blueprint.tty ? 'Yes' : 'No'}
                </DataList.Value>
              </DataList.Item>
              <DataList.Item>
                <DataList.Label>Stdin Open</DataList.Label>
                <DataList.Value>
                  {blueprint.stdin_open ? 'Yes' : 'No'}
                </DataList.Value>
              </DataList.Item>
              <DataList.Item>
                <DataList.Label>Networks</DataList.Label>
                <DataList.Value>
                  {blueprint.networks.map((n) => <Code color="gray" key={n} className="!me-1">{n}</Code>)}
                </DataList.Value>
              </DataList.Item>
            </DataList.Root>
          </Card>
        ))}
      </Grid>
    </>
  );
}
