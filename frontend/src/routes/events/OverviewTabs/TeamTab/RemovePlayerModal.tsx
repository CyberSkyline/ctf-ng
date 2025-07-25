import { Button } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbDoorExit } from 'react-icons/tb';

interface RemovePlayerModalProps {
  id: string,
  name: string,
}

export default function RemovePlayerModal({ id, name }:RemovePlayerModalProps) {
  const removePlayer = async () => {
    console.log('remove the player', id);
  };

  return (
    <Modal
      title={`Are you sure you want to remove ${name}?`}
      description="They will no longer have access to participate with this team. The invite code for the team will change."
      trigger={(
        <Button variant="soft" color="red">
          <TbDoorExit />
          Remove Player
        </Button>
      )}
      onSubmit={removePlayer}
      submitVerb="Remove"
      submitColor="red"
    />
  );
}
