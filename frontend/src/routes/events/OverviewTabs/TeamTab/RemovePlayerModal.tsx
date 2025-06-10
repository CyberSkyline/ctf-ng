import { Text } from '@radix-ui/themes';
import Modal from 'components/Modal';

interface RemovePlayerModalProps {
  id: string,
  name: string,
}

export default function RemovePlayerModal({ id, name }:RemovePlayerModalProps) {
  function removePlayer() {
    console.log('remove the player', id);
  }

  return (
    <Modal
      title={`Are you sure you want to remove ${name}?`}
      buttonText="Remove"
      onSubmit={removePlayer}
      onSubmitText="Remove"
      onSubmitColor="red"
    >
      <Text>
        They will no longer have access to participate with this team.
        The invite code for the team will change.
      </Text>
    </Modal>
  );
}
