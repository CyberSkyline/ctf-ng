import { COLOR_NEGATIVE } from '@/constants';
import { banUser, unbanUser } from '@/hooks/users';
import type { AdminUser } from '@/types';
import { Button } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbHammer, TbHammerOff } from 'react-icons/tb';

export default function BanUserModal({ user }: {user: AdminUser}) {
  const unban = user.banned;
  const Icon = unban ? TbHammerOff : TbHammer;

  const handleSubmit = async () => {
    if (unban) {
      return unbanUser(user.id);
    }
    return banUser(user.id);
  };

  return (
    <Modal
      title={unban ? 'Unban User?' : 'Ban User?'}
      trigger={(
        <Button
          color={COLOR_NEGATIVE}
          variant="soft"
          disabled={!unban && user.roles.includes('admin')}
        >
          <Icon />
          {unban ? 'Unban' : 'Ban'}
        </Button>
    )}
      description={
        `${user.name} will ${unban ? '' : 'no longer '}be able to access the platform${unban ? ' again' : ''}.
        ${unban ? '' : 'They will not be removed from any teams unless done manually by an admin.'}`
      }
      onSubmit={handleSubmit}
      submitVerb={unban ? 'Unban' : 'Ban'}
      submitColor={COLOR_NEGATIVE}
    />
  );
}
