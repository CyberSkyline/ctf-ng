import { useAdminChallengeBlueprints } from '@/hooks/challenge';
import {
  Button,
  Card,
  Code,
  DataList,
  Heading,
} from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';

export default function ChallengeBlueprintTab({ challengeId }: {challengeId: number}) {
  const { data : blueprints, error } = useAdminChallengeBlueprints(challengeId);

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  return blueprints?.map((blueprint) => (
    <Card key={blueprint.id}>
      <Heading>{blueprint.hostname}</Heading>
      <DataList.Root className="!gap-1 !mt-3">
        <DataList.Item>
          <DataList.Label>Image</DataList.Label>
          <DataList.Value>
            {blueprint.image}
            <Button variant="ghost" className="!ml-2">Re-pull</Button>
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
  ));
}
