import { COLOR_HINT } from '@/constants';
import { impersonateUser, useCurrentUser } from '@/hooks/users';
import type { User } from '@/types';
import { Button } from '@radix-ui/themes';
import { TbGhost } from 'react-icons/tb';

export default function ImpersonateUserButton({ user }: {user: User}) {
  const { data : currentUser } = useCurrentUser();
  const handleImpersonate = () => impersonateUser(user.id);

  return (
    <Button
      variant="soft"
      color={COLOR_HINT}
      onClick={handleImpersonate}
      disabled={currentUser?.id === user.id || user.roles.length > 0} // Disable for disallowed impersonation targets
    >
      <TbGhost />
      Impersonate
    </Button>
  );
}
