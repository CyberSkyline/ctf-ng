import { Button } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbStar } from 'react-icons/tb';

interface AssignCaptainModalProps {
  id: string,
  name: string,
}

export default function AssignCaptainModal({ id, name }:AssignCaptainModalProps) {
  const assignCaptain = async () => {
    console.log('assign captain', id);
  };

  return (
    <Modal
      title={`Are you sure you want to assign ${name}?`}
      description="You will no longer be a Team Captain. By assigning a new member as Team Captain, you will lose your ability to add and remove team members."
      trigger={(
        <Button variant="soft" color="lime">
          <TbStar />
          Assign Captain
        </Button>
      )}
      onSubmit={assignCaptain}
      submitVerb="Assign"
    />
  );
}
