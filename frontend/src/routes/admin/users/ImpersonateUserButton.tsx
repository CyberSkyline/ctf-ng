import { COLOR_HINT, ImpersonateIcon } from '@/constants';
import { impersonateUser, useCurrentUser } from '@/hooks/users';
import type { AdminUser } from '@/types';
import { Button } from '@radix-ui/themes';

export default function ImpersonateUserButton({ user }: {user: AdminUser}) {
  const { data : currentUser } = useCurrentUser();
  const handleImpersonate = () => impersonateUser(user.id);

  return (
    <Button
      variant="soft"
      color={COLOR_HINT}
      onClick={handleImpersonate}
      disabled={currentUser?.id === user.id || user.roles.length > 0 || user.banned} // Disable for disallowed impersonation targets
    >
      <ImpersonateIcon />
      Impersonate
    </Button>
  );
}
