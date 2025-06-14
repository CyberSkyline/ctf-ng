import { Text } from '@radix-ui/themes';
import Modal from 'components/Modal';

interface AssignCaptainModalProps {
  id: string,
  name: string,
}

export default function AssignCaptainModal({ id, name }:AssignCaptainModalProps) {
  function assignCaptain() {
    console.log('assign captain', id);
  }

  return (
    <Modal
      title={`Are you sure you want to assign ${name}?`}
      buttonText="Assign Captain"
      onSubmit={assignCaptain}
      onSubmitText="Assign"
    >
      <Text>
        You will no longer be a Team Captain. By assigning a new member as Team Captain, you will lose your ability to add and remove team members.
      </Text>
    </Modal>
  );
}
