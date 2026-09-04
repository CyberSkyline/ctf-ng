import { COLOR_NEGATIVE } from '@/constants';
import { deleteAnnouncement } from '@/hooks/announcements';
import { Button } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbTrash } from 'react-icons/tb';

export default function DeleteAnnouncementModal({ id }: {id: number}) {
  return (
    <Modal
      title="Delete Announcement"
      description="Are you sure you want to delete this announcement and any associated notifications?"
      submitVerb="Delete"
      submitColor={COLOR_NEGATIVE}
      onSubmit={async () => deleteAnnouncement(id)}
      trigger={(
        <Button
          variant="soft"
          color={COLOR_NEGATIVE}
        >
          <TbTrash />
          Delete
        </Button>
      )}
    />
  );
}
