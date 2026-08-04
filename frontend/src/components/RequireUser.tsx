import { ROUTEPREFIX } from '@/constants';
import { useAuth } from '@/hooks/users';
import type { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router';

export default function RequireUser({ children, replace }: { children: ReactNode, replace?: ReactNode }) {
  const { isAuthenticated, isUnauthenticated } = useAuth();

  const { pathname, search } = useLocation();

  if (isAuthenticated) {
    return children;
  }

  if (isUnauthenticated) {
    if (replace) {
      return replace;
    }

    return <Navigate to={`/login?redirect=${encodeURIComponent(ROUTEPREFIX + pathname + search)}`} replace />;
  }

  return null;
}
