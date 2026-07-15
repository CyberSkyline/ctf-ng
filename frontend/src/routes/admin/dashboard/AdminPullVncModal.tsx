import { COLOR_POSITIVE } from '@/constants';
import { pullVNCImage, useImagePullStatus } from '@/hooks/container';
import { Button, Flex, Text } from '@radix-ui/themes';
import ImagePullStatus from 'components/ImagePullStatus';
import Modal from 'components/Modal';
import { TbDownload } from 'react-icons/tb';

export default function AdminPullVncModal() {
  const { data : pull } = useImagePullStatus('VNC');

  const handlePull = () => pullVNCImage();

  return (
    <Flex direction="row-reverse" gap="2" align="center">
      <Modal
        title="Pull VNC Container image"
        description="This will pull the VNC container image."
        submitVerb="Pull"
        submitColor={COLOR_POSITIVE}
        onSubmit={handlePull}
        trigger={(
          <Button color={COLOR_POSITIVE} loading={pull?.status === 'pulling'}>
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
