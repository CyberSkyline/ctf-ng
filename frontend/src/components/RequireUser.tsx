import { useCurrentUser } from '@/hooks/users';
import type { ReactNode } from 'react';
import { Navigate } from 'react-router';

export default function RequireUser({ children, replace }: { children: ReactNode, replace?: ReactNode }) {
  const { data : user, error } = useCurrentUser();

  if (user) {
    return children;
  }

  if (error) {
    if (replace) {
      return replace;
    }

    return <Navigate to={`/login?redirect=${encodeURIComponent(window.location.pathname + window.location.search)}`} replace />;
  }

  return null;
}
