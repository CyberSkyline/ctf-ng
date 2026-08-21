import { COLOR_POSITIVE } from '@/constants';
import { pullVNCImage } from '@/hooks/container';
import { Button, Flex, Text } from '@radix-ui/themes';
import ImagePullStatus from 'components/ImagePullStatus';
import Modal from 'components/Modal';
import { TbDownload } from 'react-icons/tb';

export default function AdminPullVncModal() {
  return (
    <Flex direction="row-reverse" gap="2" align="center">
      <Modal
        title="Pull VNC Container image"
        description="This will pull the VNC container image."
        submitVerb="Pull"
        submitColor={COLOR_POSITIVE}
        onSubmit={pullVNCImage}
        trigger={(
          <Button color={COLOR_POSITIVE}>
            <TbDownload />
            Pull VNC Image
          </Button>
          )}
      >
        <Text color="gray">
          The workspace VNC will be pulled. All existing workspaces will need to be recycled to get the new image.
        </Text>
      </Modal>
      <ImagePullStatus id="VNC" />
    </Flex>
  );
}
