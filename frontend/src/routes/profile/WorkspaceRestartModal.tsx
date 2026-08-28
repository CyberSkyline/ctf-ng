import { COLOR_NEGATIVE } from '@/constants';
import { restartWorkspace } from '@/hooks/container';
import {
  Box,
  Button,
  Flex,
  Heading,
  Text,
} from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbReload } from 'react-icons/tb';

export default function WorkspaceRestartModal() {
  return (
    <Flex direction="column" gap="4">
      <Box>
        <Heading as="h2">Workspace</Heading>
        <Text color="gray" trim="end">Restart your challenge workspace if it becomes unresponsive.</Text>
      </Box>
      <Modal
        title="Restart Workspace"
        description="This will restart your workspace. If you need your workspace completely reset, please contact support."
        submitVerb="Restart"
        submitColor={COLOR_NEGATIVE}
        onSubmit={async () => restartWorkspace()}
        trigger={(
          <Button
            color={COLOR_NEGATIVE}
            className="!w-24"
          >
            <TbReload />
            Restart
          </Button>
        )}
      />
    </Flex>
  );
}
