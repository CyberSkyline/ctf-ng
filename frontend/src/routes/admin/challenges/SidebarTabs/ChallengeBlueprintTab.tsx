import { COLOR_NEGATIVE, COLOR_POSITIVE, COLOR_WARNING } from '@/constants';
import { apiMutation } from '@/fetchers';
import { useAdminChallengeBlueprints } from '@/hooks/challenge';
import socket from '@/socket';
import {
  Button,
  Card,
  Code,
  DataList,
  Grid,
  Spinner,
  Text,
} from '@radix-ui/themes';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import { ErrorCallout, WarningCallout } from 'components/Callouts';
import Modal from 'components/Modal';
import { useEffect, useState } from 'react';
import {
  TbCancel,
  TbCheck,
  TbDownload,
  TbPackage,
} from 'react-icons/tb';

export default function ChallengeBlueprintTab({ challengeId }: {challengeId: number}) {
  const { data : blueprints, error } = useAdminChallengeBlueprints(challengeId);

  const [ pullStates, setPullStates ] = useState<{[key: number]:'pulling' | 'success' | 'fail'}>({});
  const [ pullErrors, setPullErrors ] = useState<string[]>([]);

  const handlePull = async () => {
    setPullStates((prev) => {
      const current = { ...prev };
      (blueprints || []).forEach((bp) => {
        current[bp.id] = 'pulling';
      });
      return current;
    });
    setPullErrors([]);

    return apiMutation(`/admin/challenges/${challengeId}/pull`, {}, {
      method : 'POST',
    });
  };

  useEffect(() => {
    socket.on('pull-success', ({ id }: {id: number}) => {
      setPullStates((prev) => ({
        ...prev,
        [id] : 'success',
      }));
    });

    socket.on('pull-fail', ({ error : pullError, id }: {error: string, id: number}) => {
      setPullErrors((prev) => ([ ...prev, pullError ]));
      setPullStates((prev) => ({
        ...prev,
        [id] : 'fail',
      }));
    });

    return () => {
      socket.off('pull-success');
      socket.off('pull-fail');
    };
  }, []);

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

      {pullErrors.map((err) => (
        <ErrorCallout key={err} className="mt-2">{err}</ErrorCallout>
      ))}

      <Grid columns="2" mt="2">
        {blueprints?.map((blueprint) => (
          <Card key={blueprint.id} className="mb-3">
            <AdminSidebarHeader title={blueprint.name} icon={<TbPackage />}>
              {pullStates[blueprint.id] === 'pulling' && (<Spinner />)}
              {pullStates[blueprint.id] === 'success' && (
                <Text color={COLOR_POSITIVE}>
                  <TbCheck className="inline me-1" />
                  Pulled
                </Text>
              )}
              {pullStates[blueprint.id] === 'fail' && (
                <Text color={COLOR_NEGATIVE}>
                  <TbCancel className="inline me-1" />
                  Error
                </Text>
              )}
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
