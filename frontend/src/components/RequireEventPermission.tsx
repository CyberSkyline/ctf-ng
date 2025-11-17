import { useEventPermission } from '@/hooks/permissions';
import type { ReactNode } from 'react';
import { ErrorCallout } from './Callouts';

export default function RequireEventPermission(
  {
    children,
    permission,
    eventId,
    permissionDeniedPlaceholder,
    loadingPlaceholder,
  } : {
    children?: ReactNode,
    permission: string,
    eventId: number,
    permissionDeniedPlaceholder?: ReactNode
    loadingPlaceholder?: ReactNode
  },
) {
  const {
    granted, denied, error,
  } = useEventPermission(permission, eventId);

  if (granted) {
    return children;
  }

  if (denied) {
    return permissionDeniedPlaceholder !== undefined
      ? permissionDeniedPlaceholder
      : <ErrorCallout>Permission Denied</ErrorCallout>;
  }

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  return loadingPlaceholder;
}
